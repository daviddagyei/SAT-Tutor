from typing import TypedDict, List, Optional, Dict, Any
from pydantic import BaseModel, ValidationError
from langgraph.graph import StateGraph, START, END
import json
import re
import logging
import time
from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import ChatGoogleGenerativeAI
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Rate limiting configuration
RATE_LIMIT_DELAY = 4.5  # seconds between requests (15 RPM = 4 second intervals, adding buffer)
last_request_time = 0

# 1. Schema Model
class QARecord(BaseModel):
    id: str
    module: int
    question_number: int
    section: str
    type: str
    category: Optional[str] = None
    stimulus: str
    choices: Optional[Dict[str, str]] = None
    correct: Optional[str] = None
    
    class Config:
        # Allow the model to handle string inputs for choices and convert them
        str_strip_whitespace = True

# 2. Graph State
class GraphState(TypedDict):
    raw_pages: List[Any]
    answer_pages: List[Any]  # Separate storage for answer pages
    chunks: List[str]
    parsed: List[QARecord]
    errors: List[str]
    current_chunk_index: int
    parsing_status: str
    answer_key: Dict[int, str]  # Map question_number -> correct_answer

# 3. Nodes
def load_pdf(state: GraphState):
    """
    Loads pages from PDF files and adds them to the state.
    """
    logging.info("Starting PDF loading process...")
    
    try:
        # Load both PDF files from the pipelines directory
        current_dir = os.path.dirname(__file__)
        questions_pdf = os.path.join(current_dir, "sat-questions.pdf")
        answers_pdf = os.path.join(current_dir, "sat_answers.pdf")
        
        questions_pages = []
        answer_pages = []
        
        # Load questions PDF
        if os.path.exists(questions_pdf):
            logging.info(f"Loading questions PDF: {questions_pdf}")
            questions_loader = PyPDFLoader(questions_pdf)
            questions_pages = questions_loader.load()
            logging.info(f"Loaded {len(questions_pages)} question pages")
        else:
            error_msg = f"Questions PDF not found at {questions_pdf}"
            logging.error(error_msg)
            state["errors"].append(error_msg)
        
        # Load answers PDF  
        if os.path.exists(answers_pdf):
            logging.info(f"Loading answers PDF: {answers_pdf}")
            answers_loader = PyPDFLoader(answers_pdf)
            answer_pages = answers_loader.load()
            logging.info(f"Loaded {len(answer_pages)} answer pages")
        else:
            error_msg = f"Answers PDF not found at {answers_pdf}"
            logging.warning(error_msg)
            state["errors"].append(error_msg)
        
        state["raw_pages"] = questions_pages
        state["answer_pages"] = answer_pages
        return state
        
    except Exception as e:
        error_msg = f"Failed to load PDF files: {str(e)}"
        logging.error(error_msg)
        state["errors"].append(error_msg)
        state["raw_pages"] = []
        state["answer_pages"] = []
        return state

def parse_answer_key(state: GraphState):
    """
    Parses the answer key from the answer pages to create a mapping.
    Enhanced with better pattern matching and validation.
    """
    logging.info("Parsing answer key...")
    
    answer_key = {}
    
    if not state.get("answer_pages"):
        logging.warning("No answer pages found, skipping answer key parsing")
        state["answer_key"] = answer_key
        return state
    
    try:
        # Combine all answer page content
        answer_text = ""
        for page in state["answer_pages"]:
            answer_text += page.page_content + "\n"
        
        logging.info(f"Answer text length: {len(answer_text)} characters")
        
        # Enhanced patterns to match question number and answer
        patterns = [
            r'(\d+)\.?\s*([A-D])',  # "1. A" or "1 A"
            r'Question\s*(\d+)[:.]?\s*([A-D])',  # "Question 1: A"
            r'(\d+)\)\s*([A-D])',  # "1) A"
            r'(\d+)\s*-\s*([A-D])',  # "1 - A"
            r'(\d+)\s*:\s*([A-D])',  # "1: A"
            r'(\d+)\s+([A-D])\s',  # "1 A " with space after
            r'(\d+)\s+([A-D])$',  # "1 A" at end of line
            r'(\d+)\s+([A-D])[,.\s]',  # "1 A," or "1 A."
        ]
        
        # Try each pattern and collect matches
        all_matches = []
        for pattern in patterns:
            matches = re.findall(pattern, answer_text, re.IGNORECASE | re.MULTILINE)
            all_matches.extend(matches)
        
        # Process matches and remove duplicates
        seen_questions = set()
        for match in all_matches:
            try:
                question_num = int(match[0])
                correct_answer = match[1].upper()
                
                # Only add if we haven't seen this question number before
                if question_num not in seen_questions:
                    answer_key[question_num] = correct_answer
                    seen_questions.add(question_num)
            except (ValueError, IndexError):
                continue
        
        # Additional validation - look for common answer key formats
        if len(answer_key) < 10:  # If we didn't find many answers, try alternative approach
            logging.info("Trying alternative answer key parsing...")
            
            # Look for tabular format (e.g., "1 A  11 B  21 C")
            tabular_pattern = r'(\d+)\s*([A-D])\s*(?:\d+\s*[A-D]\s*)*'
            tabular_matches = re.findall(tabular_pattern, answer_text, re.IGNORECASE)
            
            for match in tabular_matches:
                try:
                    question_num = int(match[0])
                    correct_answer = match[1].upper()
                    if question_num not in answer_key:
                        answer_key[question_num] = correct_answer
                except (ValueError, IndexError):
                    continue
        
        logging.info(f"Parsed {len(answer_key)} answers from answer key")
        
        # Log a sample of the answer key for verification
        if answer_key:
            sample_keys = sorted(list(answer_key.keys()))[:10]
            sample_answers = {k: answer_key[k] for k in sample_keys}
            logging.info(f"Sample answers: {sample_answers}")
        
        state["answer_key"] = answer_key
        
    except Exception as e:
        error_msg = f"Failed to parse answer key: {str(e)}"
        logging.error(error_msg)
        state["errors"].append(error_msg)
        state["answer_key"] = {}
    
    return state

def split_pages(state: GraphState):
    """
    Splits the raw pages into question-based chunks for processing.
    Enhanced with better validation and logging.
    """
    logging.info("Starting page splitting process...")
    
    # If there are no pages, there's nothing to split.
    if not state.get("raw_pages"):
        logging.warning("No pages to split")
        state["chunks"] = []
        return state

    try:
        chunks = []
        total_question_chunks = 0
        total_fallback_chunks = 0
        
        for page_idx, page in enumerate(state["raw_pages"]):
            page_content = page.page_content
            logging.info(f"Processing page {page_idx + 1}/{len(state['raw_pages'])} - Length: {len(page_content)} chars")
            
            # Try to split by question numbers first
            question_chunks = split_by_question_numbers(page_content)
            
            if question_chunks:
                chunks.extend(question_chunks)
                total_question_chunks += len(question_chunks)
                logging.info(f"Found {len(question_chunks)} valid questions on page {page_idx + 1}")
            else:
                # Fallback to content-based splitting if no clear question numbers
                logging.info(f"No clear question boundaries found on page {page_idx + 1}, using content-based splitting")
                fallback_chunks = split_by_content(page_content)
                chunks.extend(fallback_chunks)
                total_fallback_chunks += len(fallback_chunks)
                logging.info(f"Generated {len(fallback_chunks)} fallback chunks from page {page_idx + 1}")
        
        logging.info(f"Split {len(state['raw_pages'])} pages into {len(chunks)} total chunks")
        logging.info(f"  - Question-based chunks: {total_question_chunks}")
        logging.info(f"  - Fallback chunks: {total_fallback_chunks}")
        
        # Sample a few chunks for validation
        if chunks:
            logging.info("Sample chunk preview:")
            for i, chunk in enumerate(chunks[:3]):
                logging.info(f"  Chunk {i+1}: {chunk[:150]}...")
        
        # Calculate estimated processing time based on actual chunk count
        estimated_time_minutes = (len(chunks) * RATE_LIMIT_DELAY) / 60
        logging.info(f"Estimated processing time: {estimated_time_minutes:.1f} minutes ({len(chunks)} chunks × {RATE_LIMIT_DELAY}s rate limit)")
        
        state["chunks"] = chunks
        
    except Exception as e:
        error_msg = f"Failed to split pages: {str(e)}"
        logging.error(error_msg)
        state["errors"].append(error_msg)
        state["chunks"] = []

    return state

def split_by_question_numbers(text: str) -> List[str]:
    """
    Splits text by question numbers with better boundary detection.
    """
    # Enhanced patterns to match question numbers
    question_patterns = [
        r'(?m)^(\d+)\.?\s+',  # "1. " at start of line
        r'(?m)^\s*(\d+)\.?\s+',  # "1. " with possible leading whitespace
        r'(?m)^Question\s+(\d+)[:.]?\s+',  # "Question 1: " or "Question 1."
        r'(?m)^Q\s*(\d+)[:.]?\s+',  # "Q1: " or "Q 1."
    ]
    
    all_matches = []
    
    # Try each pattern and collect all matches
    for pattern in question_patterns:
        matches = list(re.finditer(pattern, text))
        all_matches.extend(matches)
    
    # Sort matches by position
    all_matches = sorted(all_matches, key=lambda m: m.start())
    
    # Remove duplicates (matches at same position)
    unique_matches = []
    last_pos = -1
    for match in all_matches:
        if match.start() > last_pos + 10:  # Allow small gap to avoid duplicates
            unique_matches.append(match)
            last_pos = match.start()
    
    if len(unique_matches) < 1:
        return []  # No questions found
    
    chunks = []
    
    for i, match in enumerate(unique_matches):
        start_pos = match.start()
        
        # Find the end position (start of next question or end of text)
        if i + 1 < len(unique_matches):
            end_pos = unique_matches[i + 1].start()
        else:
            end_pos = len(text)
        
        chunk = text[start_pos:end_pos].strip()
        
        # Filter out chunks that are too short or look like headers/instructions
        if is_valid_question_chunk(chunk):
            chunks.append(chunk)
    
    return chunks

def is_valid_question_chunk(chunk: str) -> bool:
    """
    Validates if a chunk contains a complete SAT question.
    """
    # Minimum length requirement
    if len(chunk) < 100:
        return False
    
    # Must contain multiple choice options (A, B, C, D)
    choice_pattern = r'[A-D][\)\.]\s+'
    choices_found = len(re.findall(choice_pattern, chunk))
    
    if choices_found < 3:  # At least 3 choices (sometimes D might be cut off)
        return False
    
    # Exclude common non-question patterns
    exclusion_patterns = [
        r'(?i)directions?[:.]',
        r'(?i)instructions?[:.]',
        r'(?i)section\s+\d+',
        r'(?i)module\s+\d+',
        r'(?i)time\s*:\s*\d+',
        r'(?i)calculator\s+(allowed|not\s+allowed)',
        r'(?i)reading\s+and\s+writing',
        r'(?i)math\s+section',
        r'(?i)answer\s+sheet',
        r'(?i)sample\s+questions?',
        r'(?i)practice\s+test',
    ]
    
    for pattern in exclusion_patterns:
        if re.search(pattern, chunk[:200]):  # Check first 200 chars
            return False
    
    return True

def split_by_content(text: str) -> List[str]:
    """
    Fallback content-based splitting when question numbers aren't clear.
    Uses conservative approach to avoid breaking questions.
    """
    # Use a more conservative approach for content splitting
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=4000,  # Larger chunks to avoid splitting questions
        chunk_overlap=500,  # More overlap to maintain context
        length_function=len,
        separators=["\n\n\n", "\n\n", "\n", ". ", "? ", "! ", "; ", ": ", " "]
    )
    
    chunks = text_splitter.split_text(text)
    
    # Filter chunks to only include those that might contain questions
    valid_chunks = []
    for chunk in chunks:
        if is_valid_question_chunk(chunk):
            valid_chunks.append(chunk)
        else:
            logging.info(f"Filtered out non-question chunk: {chunk[:100]}...")
    
    return valid_chunks

def llm_extract(state: GraphState):
    """
    Uses LLM reasoning to parse and extract structured data from chunks.
    Includes rate limiting and robust parsing with fallback mechanisms.
    """
    global last_request_time
    
    # Rate limiting - ensure we don't exceed 15 RPM for free tier
    current_time = time.time()
    time_since_last_request = current_time - last_request_time
    if time_since_last_request < RATE_LIMIT_DELAY:
        sleep_time = RATE_LIMIT_DELAY - time_since_last_request
        logging.info(f"Rate limiting: sleeping for {sleep_time:.2f} seconds")
        time.sleep(sleep_time)
    
    chunk = state["chunks"][state["current_chunk_index"]]
    chunk_info = f"chunk {state['current_chunk_index'] + 1}/{len(state['chunks'])}"
    
    # Calculate progress and estimated time remaining
    progress_percent = ((state["current_chunk_index"] + 1) / len(state["chunks"])) * 100
    remaining_chunks = len(state["chunks"]) - state["current_chunk_index"] - 1
    estimated_time_remaining = (remaining_chunks * RATE_LIMIT_DELAY) / 60
    
    logging.info(f"Processing {chunk_info} ({progress_percent:.1f}%) - ETA: {estimated_time_remaining:.1f} min - Length: {len(chunk)} chars")
    
    # Update the request time
    last_request_time = time.time()
    
    try:
        # Initialize Gemini client
        llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0)
        
        # Generate a unique ID for this chunk
        unique_id = f"SAT-Q{state['current_chunk_index'] + 1:03d}"
        
        # Create a more specific prompt with math formatting awareness
        prompt = f"""You are an expert at extracting structured data from SAT questions found in PDF text.

Your task is to identify a complete SAT question in the given text chunk and extract it as structured JSON.

IMPORTANT RULES:
1. Only extract data if you can identify a complete question with answer choices
2. If the text chunk doesn't contain a complete question, return null for choices and stimulus fields
3. The choices field must be either null or a valid JSON object with keys "A", "B", "C", "D"
4. Never return choices as a string - always as an object or null
5. Extract the actual question number from the text, not just "1"
6. Include all relevant context in the stimulus field
7. For math problems, preserve mathematical notation as plain text (e.g., "x^2", "√5", "π")
8. Handle special characters by using plain text equivalents
9. Preserve line breaks and formatting within the stimulus and choices

MATH FORMATTING GUIDELINES:
- Use plain text for mathematical expressions: x^2, √5, π, ∞, ≤, ≥, ≠
- Preserve fractions as text: 1/2, 3/4, (x+1)/(x-1)
- Keep equations readable: 2x + 3 = 7, y = mx + b
- Maintain spacing and structure for readability

Extract the following information and return ONLY valid JSON:
{{
  "id": "{unique_id}",
  "module": <integer>,
  "question_number": <integer>,
  "section": "<string>",
  "type": "MC",
  "category": "<string or null>",
  "stimulus": "<complete question text or null>",
  "choices": {{"A": "text", "B": "text", "C": "text", "D": "text"}} or null,
  "correct": null
}}

Examples of valid responses:
1. Complete question:
{{
  "id": "{unique_id}",
  "module": 1,
  "question_number": 15,
  "section": "Reading and Writing",
  "type": "MC",
  "category": "Craft and Structure",
  "stimulus": "The author uses the word 'resilient' in line 12 primarily to...",
  "choices": {{"A": "emphasize the durability of the material", "B": "highlight the adaptive nature of the system", "C": "contrast with earlier descriptions", "D": "introduce a new concept"}},
  "correct": null
}}

2. Math question example:
{{
  "id": "{unique_id}",
  "module": 1,
  "question_number": 22,
  "section": "Math",
  "type": "MC",
  "category": null,
  "stimulus": "If 2x + 3 = 11, what is the value of x?",
  "choices": {{"A": "2", "B": "4", "C": "6", "D": "8"}},
  "correct": null
}}

3. No complete question found:
{{
  "id": "{unique_id}",
  "module": 1,
  "question_number": 1,
  "section": "Unknown",
  "type": "MC",
  "category": null,
  "stimulus": null,
  "choices": null,
  "correct": null
}}

Text to extract from:
{chunk}

Return ONLY the JSON object, no other text:"""
        
        # Invoke the LLM with the prompt
        response = llm.invoke(prompt)
        
        # Parse the response manually
        response_content = response.content.strip()
        
        # Clean up the response to extract JSON
        json_match = re.search(r'\{.*\}', response_content, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
            
            # Clean the JSON string to handle escape issues
            json_str = clean_json_string(json_str)
            
            try:
                record_dict = json.loads(json_str)
                
                # Validate and clean the record
                record_dict = validate_and_clean_record(record_dict, unique_id)
                
                # Create QARecord from the cleaned dictionary
                record = QARecord(**record_dict)
                
                # Try to extract actual question number from the chunk
                actual_question_number = extract_question_number(chunk)
                if actual_question_number:
                    record.question_number = actual_question_number
                
                # If we have an answer key, try to fill in the correct answer
                if state.get("answer_key") and record.question_number in state["answer_key"]:
                    record.correct = state["answer_key"][record.question_number]
                    logging.info(f"Added correct answer '{record.correct}' for question {record.question_number}")
                
                state["parsed"].append(record)
                state["parsing_status"] = "success"
                logging.info(f"Successfully extracted question: {record.id} (Q{record.question_number})")
                return state
                
            except json.JSONDecodeError as e:
                logging.error(f"JSON parsing failed for {chunk_info}: {str(e)}")
                logging.error(f"Raw JSON: {json_str[:200]}...")
                raise Exception(f"JSON parsing failed: {str(e)}")
        else:
            raise Exception("No JSON found in LLM response")
        
    except Exception as e:
        error_msg = f"LLM extraction failed for {chunk_info}: {str(e)}"
        logging.error(error_msg)
        state["errors"].append(error_msg)
        state["parsing_status"] = "failure"
        return state

def clean_json_string(json_str: str) -> str:
    """
    Cleans JSON string to handle common escape issues from PDF text.
    """
    # Fix common escape issues
    json_str = json_str.replace('\\n', '\\n')  # Ensure proper newline escaping
    json_str = json_str.replace('\\"', '\\"')  # Ensure proper quote escaping
    json_str = json_str.replace('\\\\', '\\')  # Fix double backslashes
    json_str = json_str.replace('\\/', '/')    # Fix escaped forward slashes
    
    # Handle problematic characters that often cause JSON parsing issues
    json_str = json_str.replace('\\u', '\\u')  # Ensure unicode escapes are proper
    json_str = json_str.replace('\\t', '\\t')  # Ensure tab escaping
    json_str = json_str.replace('\\r', '\\r')  # Ensure carriage return escaping
    
    return json_str

def validate_and_clean_record(record_dict: dict, unique_id: str) -> dict:
    """
    Validates and cleans the record dictionary from LLM output.
    """
    # Ensure required fields exist
    record_dict["id"] = unique_id  # Always use our generated ID
    record_dict["module"] = record_dict.get("module", 1)
    record_dict["question_number"] = record_dict.get("question_number", 1)
    record_dict["section"] = record_dict.get("section", "Unknown")
    record_dict["type"] = record_dict.get("type", "MC")
    record_dict["category"] = record_dict.get("category")
    record_dict["stimulus"] = record_dict.get("stimulus")
    record_dict["correct"] = record_dict.get("correct")
    
    # Handle choices field - ensure it's either None or a proper dict
    choices = record_dict.get("choices")
    if choices is not None:
        if isinstance(choices, str):
            # If choices is a string, try to parse it or set to None
            try:
                choices = json.loads(choices)
            except:
                choices = None
        elif isinstance(choices, dict):
            # Validate that it has the right structure
            expected_keys = {"A", "B", "C", "D"}
            if not all(key in choices for key in expected_keys):
                choices = None
        else:
            choices = None
    
    record_dict["choices"] = choices
    return record_dict

def extract_question_number(text: str) -> Optional[int]:
    """
    Extracts the actual question number from the text.
    """
    # Try various patterns to find question numbers
    patterns = [
        r'(?m)^(\d+)\.?\s+',  # "1. " at start of line
        r'(?m)^\s*(\d+)\.?\s+',  # "1. " with possible leading whitespace
        r'(?m)^Question\s+(\d+)[:.]?\s+',  # "Question 1: " or "Question 1."
        r'(?m)^Q\s*(\d+)[:.]?\s+',  # "Q1: " or "Q 1."
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            try:
                return int(match.group(1))
            except:
                continue
    
    return None

def llm_fallback(state: GraphState):
    """
    Fallback processing for failed chunks - marks them and continues.
    """
    chunk_info = f"chunk {state['current_chunk_index'] + 1}/{len(state['chunks'])}"
    error_msg = f"Skipping {chunk_info} due to parsing failure"
    logging.warning(error_msg)
    state["errors"].append(error_msg)
    state["parsing_status"] = "failure"
    return state

def assemble_json(state: GraphState):
    """
    Assembles the parsed data into a JSON file.
    This node will now simply pass through the state. 
    The actual file writing will happen once at the end.
    """
    # Increment the chunk index to move to the next chunk
    state["current_chunk_index"] += 1
    
    # Log progress every 10 chunks
    if state["current_chunk_index"] % 10 == 0:
        logging.info(f"Processed {state['current_chunk_index']}/{len(state['chunks'])} chunks")
    
    return state

def should_continue(state: GraphState):
    """
    Determines whether to continue processing chunks.
    """
    if state["current_chunk_index"] < len(state["chunks"]):
        return "continue"
    else:
        return "end"

# 4. Graph Definition
workflow = StateGraph(GraphState)

workflow.add_node("load_pdf", load_pdf)
workflow.add_node("parse_answer_key", parse_answer_key)
workflow.add_node("split_pages", split_pages)
workflow.add_node("llm_extract_node", llm_extract)
workflow.add_node("llm_fallback_node", llm_fallback)
workflow.add_node("assemble_json", assemble_json)

workflow.set_entry_point("load_pdf")
workflow.add_edge("load_pdf", "parse_answer_key")
workflow.add_edge("parse_answer_key", "split_pages")

# Add a conditional edge for early termination if no chunks are found
workflow.add_conditional_edges(
    "split_pages",
    lambda state: "end" if not state.get("chunks") else "continue",
    {
        "continue": "llm_extract_node",
        "end": END
    }
)

workflow.add_conditional_edges(
    "llm_extract_node",
    lambda state: state["parsing_status"],
    {
        "success": "assemble_json",
        "failure": "llm_fallback_node"
    }
)

workflow.add_edge("llm_fallback_node", "assemble_json")

workflow.add_conditional_edges(
    "assemble_json",
    should_continue,
    {
        "continue": "llm_extract_node",
        "end": END
    }
)


# 5. Run the graph
if __name__ == "__main__":
    logging.info("Starting SAT Question Ingestion Pipeline")
    
    app = workflow.compile()  # LangGraph handles recursion internally
    initial_state = {
        "raw_pages": [],
        "answer_pages": [],
        "chunks": [],
        "parsed": [],
        "errors": [],
        "current_chunk_index": 0,
        "parsing_status": "",
        "answer_key": {}
    }
    
    logging.info("Invoking pipeline workflow...")
    
    # Calculate estimated time based on rate limits
    estimated_chunks = 100  # Initial estimate, will be updated after splitting
    estimated_time_minutes = (estimated_chunks * RATE_LIMIT_DELAY) / 60
    logging.info(f"Estimated processing time: {estimated_time_minutes:.1f} minutes (based on rate limits)")
    
    final_state = app.invoke(initial_state, {"recursion_limit": 500})

    # Write the final assembled JSON to the output file
    try:
        output_path = os.path.join(os.path.dirname(__file__), "output.ndjson")
        with open(output_path, "w") as f:
            for record in final_state.get('parsed', []):
                # Handle both Pydantic models and dicts
                if hasattr(record, 'model_dump'):
                    f.write(json.dumps(record.model_dump()) + "\n")
                elif hasattr(record, 'dict'):
                    f.write(json.dumps(record.dict()) + "\n")
                else:
                    f.write(json.dumps(record) + "\n")
        logging.info(f"Output written to: {output_path}")
    except Exception as e:
        logging.error(f"Failed to write output file: {str(e)}")

    # Final reporting
    logging.info("Pipeline finished.")
    logging.info(f"Successfully parsed: {len(final_state.get('parsed', []))}")
    logging.info(f"Answer key entries: {len(final_state.get('answer_key', {}))}")
    logging.info(f"Errors: {len(final_state.get('errors', []))}")
    
    if final_state.get('errors'):
        logging.warning("Error details:")
        for error in final_state['errors']:
            logging.warning(f"  - {error}")
    
    # Summary statistics
    parsed_records = final_state.get('parsed', [])
    if parsed_records:
        sections = {}
        for record in parsed_records:
            section = record.section if hasattr(record, 'section') else record.get('section', 'Unknown')
            sections[section] = sections.get(section, 0) + 1
        
        logging.info("Questions by section:")
        for section, count in sections.items():
            logging.info(f"  - {section}: {count}")
    
    logging.info("Pipeline execution complete.")
