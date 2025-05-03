"""
API endpoints for practice-related functionality
"""
import json
import os
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse

from ....models.question import QuestionType
from ....services.learning_service import LearningService
from ...deps import get_learning_service, get_current_user
from ...schemas.question import PracticeSessionSchema, QuestionSchema

router = APIRouter()

# Path to extracted questions JSON file
EXTRACTED_QUESTIONS_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))), 
                                      "backend/tests/utils/unit/pdf_processing/output/extracted_text.json")

# Let's also define a fallback path in case the first one doesn't work
FALLBACK_PATH = "/home/iamdankwa/SAT-Tutor-2/backend/tests/utils/unit/pdf_processing/output/extracted_text.json"

@router.get("/sat-questions", response_model=List[Dict[str, Any]])
async def get_sat_questions(
    module: Optional[str] = Query(None, description="Filter by module number (1 or 2)"),
    question_type: Optional[str] = Query(None, description="Filter by question type"),
    current_user: Dict = Depends(get_current_user)
):
    """
    Get SAT questions extracted from the PDF
    """
    try:
        # Try the first path
        if os.path.exists(EXTRACTED_QUESTIONS_PATH):
            with open(EXTRACTED_QUESTIONS_PATH, 'r') as f:
                extracted_data = json.load(f)
        # If first path fails, try the fallback path
        elif os.path.exists(FALLBACK_PATH):
            with open(FALLBACK_PATH, 'r') as f:
                extracted_data = json.load(f)
        else:
            raise FileNotFoundError(f"Could not find the extracted questions file at {EXTRACTED_QUESTIONS_PATH} or {FALLBACK_PATH}")
        
        # Process the extracted data into proper question format
        questions = []
        
        for page_num, page_content in extracted_data.items():
            # Parse the page content to extract questions
            # This parsing is simplified and may need to be adjusted based on the actual format
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
                # Simple parsing logic - this would need to be more sophisticated in production
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
                    continue
        
        # Filter questions if needed
        return questions
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing questions: {str(e)}")

@router.post("/record-progress", response_model=Dict[str, Any])
async def record_practice_progress(
    data: Dict[str, Any],
    learning_service: LearningService = Depends(get_learning_service),
    current_user: Dict = Depends(get_current_user)
):
    """
    Record progress from a practice session
    """
    try:
        topic_id = data.get("topic_id", "sat-general")
        correct = data.get("correct", False)
        
        # Update user progress using the learning service
        await learning_service.update_practice_progress(
            user_id=current_user["id"],
            topic_id=topic_id,
            completed=True,
            correct=correct
        )
        
        return {
            "success": True,
            "message": "Progress recorded successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error recording progress: {str(e)}")