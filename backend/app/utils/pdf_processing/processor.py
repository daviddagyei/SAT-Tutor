"""
Text Processing Module for SAT Questions

This module processes extracted text from PDFs to identify SAT question sections
(MATH, READING AND WRITING) and individual questions within those sections.
"""
import re
import logging
from enum import Enum
from typing import Dict, List, Tuple, Optional, Any

logger = logging.getLogger(__name__)

class SATSection(str, Enum):
    """SAT Test Section Types"""
    MATH = "MATH"
    READING_WRITING = "READING_WRITING"
    UNKNOWN = "UNKNOWN"


def process_text_to_sections(text_by_page: Dict[int, str]) -> Dict[SATSection, List[str]]:
    """
    Process text extracted from PDFs and organize it into SAT sections
    
    Args:
        text_by_page: Dictionary mapping page numbers to extracted text
        
    Returns:
        Dictionary mapping section types to lists of content blocks
    """
    combined_text = "\n".join(text_by_page.values())
    
    # Initial section detection
    sections = {}
    current_section = SATSection.UNKNOWN
    current_content = []
    
    # Common section header patterns in SAT tests
    math_patterns = [
        r"Math Test[:\s]*No Calculator",
        r"Math Test[:\s]*Calculator",
        r"Math Section",
        r"MATH TEST"
    ]
    
    reading_writing_patterns = [
        r"Reading Test",
        r"Writing and Language Test",
        r"Reading and Writing",
        r"Reading and Writing Section",
        r"READING AND WRITING"
    ]
    
    # Process the text line by line to identify sections
    for line in combined_text.split('\n'):
        line = line.strip()
        
        # Skip empty lines
        if not line:
            continue
            
        # Check for section headers
        if any(re.search(pattern, line, re.IGNORECASE) for pattern in math_patterns):
            if current_content and current_section != SATSection.UNKNOWN:
                if current_section not in sections:
                    sections[current_section] = []
                sections[current_section].append('\n'.join(current_content))
                
            current_section = SATSection.MATH
            current_content = [line]
            
        elif any(re.search(pattern, line, re.IGNORECASE) for pattern in reading_writing_patterns):
            if current_content and current_section != SATSection.UNKNOWN:
                if current_section not in sections:
                    sections[current_section] = []
                sections[current_section].append('\n'.join(current_content))
                
            current_section = SATSection.READING_WRITING
            current_content = [line]
            
        else:
            current_content.append(line)
    
    # Add the last section if it exists
    if current_content and current_section != SATSection.UNKNOWN:
        if current_section not in sections:
            sections[current_section] = []
        sections[current_section].append('\n'.join(current_content))
    
    return sections


def extract_questions_from_section(section_text: str, section_type: SATSection) -> List[Dict[str, Any]]:
    """
    Extract individual questions from a section's text
    
    Args:
        section_text: The text content of a section
        section_type: The type of section (MATH, READING_WRITING)
        
    Returns:
        List of dictionaries containing question data
    """
    questions = []
    
    if section_type == SATSection.MATH:
        questions = extract_math_questions(section_text)
    elif section_type == SATSection.READING_WRITING:
        questions = extract_reading_writing_questions(section_text)
    
    return questions


def extract_math_questions(text: str) -> List[Dict[str, Any]]:
    """
    Extract math questions from text
    
    Args:
        text: Text containing math questions
        
    Returns:
        List of dictionaries containing question data
    """
    questions = []
    
    # Pattern to identify math questions (question numbers followed by text)
    question_pattern = r"(\d+)[\.|\)](.+?)(?=\d+[\.|\)]|$)"
    
    # Modified pattern for multiple choice options to better capture all options
    option_pattern = r"([A-D])[\.|\)](.+?)(?=[A-D][\.|\)]|$|\n\s*\n)"
    
    # Find all questions
    matches = re.finditer(question_pattern, text, re.DOTALL)
    
    for match in matches:
        question_number = match.group(1)
        question_text = match.group(2).strip()
        
        # Check if it's multiple choice
        options = []
        
        # Extract all options with modified approach
        option_matches = re.findall(r"([A-D])[\.|\)]\s*([^\n]*(?:\n(?![A-D][\.|\)])[^\n]*)*)", question_text)
        
        for option_letter, option_content in option_matches:
            options.append({
                "id": option_letter,
                "text": option_content.strip(),
                "is_correct": None  # We don't know the correct answer yet
            })
            
        # Determine question type
        question_type = "multiple_choice" if options else "grid_in"
        
        # Extract the main question without the options for multiple choice
        if options:
            # Extract just the question part by removing option text
            main_question = re.split(r"[A-D][\.|\)]", question_text)[0].strip()
        else:
            main_question = question_text
            
        questions.append({
            "question_number": question_number,
            "text": main_question,
            "options": options,
            "question_type": question_type,
            "section": SATSection.MATH,
            "topic_id": "",  # To be determined later
            "difficulty": 3,  # Default difficulty, can be adjusted later
            "answer": "",  # To be filled later
            "explanation": "",  # To be filled later
        })
    
    return questions


def extract_reading_writing_questions(text: str) -> List[Dict[str, Any]]:
    """
    Extract reading and writing questions from text
    
    Args:
        text: Text containing reading and writing questions
        
    Returns:
        List of dictionaries containing question data
    """
    questions = []
    
    # For Reading & Writing, we need to extract passages first
    passage_pattern = r"((?:^|\n)(?:[A-Z][^.!?]*[.!?]){3,})"
    passages = re.findall(passage_pattern, text)
    passage_text = "\n\n".join(passages) if passages else ""
    
    # Then look for questions that may reference these passages
    question_pattern = r"(\d+)[\.|\)](.+?)(?=\d+[\.|\)]|$)"
    
    # Find all questions
    matches = re.finditer(question_pattern, text, re.DOTALL)
    
    for match in matches:
        question_number = match.group(1)
        question_text = match.group(2).strip()
        
        # Extract all options with modified approach
        options = []
        option_matches = re.findall(r"([A-D])[\.|\)]\s*([^\n]*(?:\n(?![A-D][\.|\)])[^\n]*)*)", question_text)
        
        for option_letter, option_content in option_matches:
            options.append({
                "id": option_letter,
                "text": option_content.strip(),
                "is_correct": None
            })
            
        # Extract the main question without the options for multiple choice
        if options:
            # Extract just the question part by removing option text
            main_question = re.split(r"[A-D][\.|\)]", question_text)[0].strip()
        else:
            main_question = question_text
            
        # Determine question type
        if "According to the passage" in main_question:
            question_type = "reading_comprehension"
        elif "evidence" in main_question.lower() or "support" in main_question.lower():
            question_type = "evidence_based"
        else:
            question_type = "multiple_choice"
            
        # Add the question with context
        question_data = {
            "question_number": question_number,
            "text": main_question,
            "options": options,
            "question_type": question_type,
            "section": SATSection.READING_WRITING,
            "topic_id": "",
            "difficulty": 3,
            "answer": "",
            "explanation": "",
        }
        
        # Always include passage as context if available
        if passage_text:
            question_data["context"] = passage_text
            
        questions.append(question_data)
    
    return questions