"""
Data Transformer Module

This module transforms extracted question data into the application's data models.
"""
import uuid
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from ...models.question import Question, QuestionType

logger = logging.getLogger(__name__)

# Topic ID mapping (these would ideally come from your database)
TOPIC_MAP = {
    "MATH": {
        "algebra": "algebra_topic_id",
        "geometry": "geometry_topic_id",
        "statistics": "statistics_topic_id",
        "problem_solving": "problem_solving_topic_id",
        # Add more math topics as needed
    },
    "READING_WRITING": {
        "reading_comprehension": "reading_comprehension_topic_id",
        "grammar": "grammar_topic_id",
        "vocabulary": "vocabulary_topic_id",
        "writing": "writing_topic_id",
        # Add more reading/writing topics as needed
    }
}

def map_question_type(raw_type: str) -> QuestionType:
    """
    Map raw question type string to QuestionType enum
    
    Args:
        raw_type: The raw question type string from extraction
        
    Returns:
        Corresponding QuestionType enum value
    """
    type_map = {
        "multiple_choice": QuestionType.MULTIPLE_CHOICE,
        "grid_in": QuestionType.GRID_IN,
        "evidence_based": QuestionType.EVIDENCE_BASED,
        "reading_comprehension": QuestionType.READING_COMPREHENSION,
    }
    
    return type_map.get(raw_type, QuestionType.MULTIPLE_CHOICE)

def assign_topic(question: Dict[str, Any]) -> str:
    """
    Assign a topic ID to a question based on content analysis
    
    Args:
        question: The question data dictionary
        
    Returns:
        A topic ID
    """
    # This is a simplified topic assignment - in a real implementation,
    # you'd use NLP or keyword matching to determine the appropriate topic
    
    section = question.get("section", "")
    text = question.get("text", "").lower()
    
    if section == "MATH":
        if any(kw in text for kw in ["equation", "solve", "expression", "variable"]):
            return TOPIC_MAP["MATH"]["algebra"]
        elif any(kw in text for kw in ["angle", "triangle", "circle", "rectangle"]):
            return TOPIC_MAP["MATH"]["geometry"]
        elif any(kw in text for kw in ["probability", "average", "mean", "median"]):
            return TOPIC_MAP["MATH"]["statistics"]
        else:
            return TOPIC_MAP["MATH"]["problem_solving"]
    else:  # READING_WRITING
        if "comprehension" in question.get("question_type", ""):
            return TOPIC_MAP["READING_WRITING"]["reading_comprehension"]
        elif any(kw in text for kw in ["grammar", "punctuation", "sentence"]):
            return TOPIC_MAP["READING_WRITING"]["grammar"]
        elif any(kw in text for kw in ["vocabulary", "meaning", "definition"]):
            return TOPIC_MAP["READING_WRITING"]["vocabulary"]
        else:
            return TOPIC_MAP["READING_WRITING"]["writing"]

def transform_to_question_model(extracted_question: Dict[str, Any]) -> Question:
    """
    Transform extracted question data into Question model instance
    
    Args:
        extracted_question: Dictionary containing extracted question data
        
    Returns:
        Question model instance
    """
    # Get or assign a topic ID
    topic_id = extracted_question.get("topic_id") or assign_topic(extracted_question)
    
    # Map question type
    question_type = map_question_type(extracted_question.get("question_type", "multiple_choice"))
    
    # Prepare options for multiple choice questions
    options = None
    if question_type == QuestionType.MULTIPLE_CHOICE:
        options = []
        raw_options = extracted_question.get("options", [])
        
        for opt in raw_options:
            options.append({
                "id": opt.get("id", ""),
                "text": opt.get("text", ""),
                "is_correct": opt.get("is_correct", False)
            })
    
    # Generate a unique ID if not provided
    question_id = extracted_question.get("id") or str(uuid.uuid4())
    
    # Create the Question model instance
    question = Question(
        topic_id=topic_id,
        question_type=question_type,
        content=extracted_question.get("text", ""),
        answer=extracted_question.get("answer", ""),
        explanation=extracted_question.get("explanation", ""),
        difficulty=extracted_question.get("difficulty", 3),
        options=options,
        tags=extracted_question.get("tags", []),
        id=question_id
    )
    
    return question

def transform_questions_to_json(questions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Transform a list of extracted questions to JSON format for database import
    
    Args:
        questions: List of dictionaries containing extracted question data
        
    Returns:
        List of question dictionaries in JSON format
    """
    result = []
    
    for q in questions:
        # Get or assign a topic ID
        topic_id = q.get("topic_id") or assign_topic(q)
        
        # Format options for multiple choice questions
        options = []
        for opt in q.get("options", []):
            options.append({
                "id": opt.get("id", ""),
                "text": opt.get("text", ""),
                "is_correct": opt.get("is_correct", False)
            })
            
        # Create JSON representation
        question_json = {
            "id": q.get("id") or str(uuid.uuid4()),
            "text": q.get("text", ""),
            "topic_id": topic_id,
            "question_type": q.get("question_type", "multiple_choice"),
            "difficulty": q.get("difficulty", 3),
            "options": options,
            "answer": q.get("answer", ""),
            "explanation": q.get("explanation", ""),
            "tags": q.get("tags", []),
            "section": q.get("section", "")
        }
        
        # Include passage context if available (for reading questions)
        if "context" in q:
            question_json["context"] = q["context"]
            
        result.append(question_json)
    
    return result