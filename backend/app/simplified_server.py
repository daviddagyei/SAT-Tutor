"""
Simplified FastAPI server for serving SAT practice questions without database dependencies.
"""

import json
import os
from typing import Dict, List, Any, Optional
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="SAT Practice API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Path to extracted questions JSON file
EXTRACTED_QUESTIONS_PATH = "/home/iamdankwa/SAT-Tutor-2/backend/tests/utils/unit/pdf_processing/output/extracted_text.json"

@app.get("/")
async def root():
    return {"message": "Welcome to SAT Practice API"}

@app.get("/api/v1/practice/sat-questions", response_model=List[Dict[str, Any]])
async def get_sat_questions(
    module: Optional[str] = Query(None, description="Filter by module number (1 or 2)"),
    question_type: Optional[str] = Query(None, description="Filter by question type")
):
    """
    Get SAT questions extracted from the PDF without requiring authentication
    """
    try:
        # Check if the file exists
        if not os.path.exists(EXTRACTED_QUESTIONS_PATH):
            raise HTTPException(status_code=404, detail=f"Extracted questions file not found at {EXTRACTED_QUESTIONS_PATH}")
        
        with open(EXTRACTED_QUESTIONS_PATH, 'r') as f:
            extracted_data = json.load(f)
        
        # Process the extracted data into proper question format
        questions = []
        
        for page_num, page_content in extracted_data.items():
            # Parse the page content to extract questions
            lines = page_content.split('\n')
            question_blocks = []
            current_block = []
            
            for line in lines:
                if line.strip().startswith(str(len(questions) + 1)):
                    if current_block:
                        question_blocks.append(current_block)
                        current_block = []
                current_block.append(line.strip())
            
            if current_block:
                question_blocks.append(current_block)
            
            # Process each question block
            for block in question_blocks:
                # Simple parsing logic 
                question_content = ' '.join(block).strip()
                
                # Extract question number, question text, and answer choices
                try:
                    question_number = int(block[0].split()[0])
                    question_text = ' '.join([line for line in block if not line.startswith('A)') and not line.startswith('B)') and not line.startswith('C)') and not line.startswith('D)')])
                    
                    choices = {}
                    for line in block:
                        if line.startswith('A)'):
                            choices['A'] = line.replace('A)', '').strip()
                        elif line.startswith('B)'):
                            choices['B'] = line.replace('B)', '').strip()
                        elif line.startswith('C)'):
                            choices['C'] = line.replace('C)', '').strip()
                        elif line.startswith('D)'):
                            choices['D'] = line.replace('D)', '').strip()
                    
                    # Determine question type based on content
                    q_type = "math" if "Module \n1" in question_content else "reading" if "Module \n2" in question_content else "unknown"
                    
                    if question_type and q_type != question_type:
                        continue
                    
                    if module:
                        if module == "1" and "Module \n1" not in question_content:
                            continue
                        elif module == "2" and "Module \n2" not in question_content:
                            continue
                    
                    questions.append({
                        "id": f"sat-q-{page_num}-{question_number}",
                        "number": question_number,
                        "type": q_type,
                        "content": question_text,
                        "choices": choices,
                        "correctAnswer": "A",  # Default, would need actual answer data
                        "explanation": "Explanation would be provided here."
                    })
                except Exception as e:
                    # Skip questions that couldn't be parsed properly
                    print(f"Error parsing question block: {e}")
                    continue
        
        return questions
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing questions: {str(e)}")

@app.post("/api/v1/practice/record-progress")
async def record_practice_progress(data: Dict[str, Any]):
    """
    Mock endpoint for recording practice progress (without database)
    """
    return {
        "success": True,
        "message": f"Progress recorded successfully (mock). Topic: {data.get('topic_id')}, Correct: {data.get('correct')}"
    }

# Run with: uvicorn app.simplified_server:app --reload --host 0.0.0.0 --port 8000