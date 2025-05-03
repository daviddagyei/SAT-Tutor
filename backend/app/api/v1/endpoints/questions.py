"""
API endpoints for questions
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Path
from fastapi.responses import JSONResponse

from ....models.question import QuestionType
from ....services.learning_service import LearningService
from ...schemas.question import (
    QuestionSchema, 
    QuestionDetailSchema,
    PracticeSessionCreateSchema,
    PracticeSessionSchema,
    QuestionAnswerSchema
)
from ...deps import get_learning_service

router = APIRouter()


@router.get("/", response_model=List[QuestionSchema])
async def get_questions(
    topic_id: Optional[str] = Query(None, description="Filter questions by topic ID"),
    difficulty: Optional[int] = Query(None, description="Filter questions by difficulty level"),
    question_type: Optional[str] = Query(None, description="Filter questions by type"),
    tags: Optional[List[str]] = Query(None, description="Filter questions by tags"),
    limit: int = Query(20, description="Maximum number of questions to return"),
    skip: int = Query(0, description="Number of questions to skip"),
    learning_service: LearningService = Depends(get_learning_service)
):
    """
    Get a list of questions with optional filtering
    """
    # Convert string question_type to enum if provided
    question_type_enum = None
    if question_type:
        try:
            question_type_enum = QuestionType(question_type)
        except ValueError:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid question type. Valid types are: {', '.join([t.value for t in QuestionType])}"
            )
    
    questions = await learning_service.get_questions(
        topic_id=topic_id,
        difficulty=difficulty,
        question_type=question_type_enum,
        tags=tags,
        limit=limit,
        skip=skip
    )
    
    return questions


@router.get("/{question_id}", response_model=QuestionDetailSchema)
async def get_question(
    question_id: str = Path(..., description="The ID of the question to retrieve"),
    learning_service: LearningService = Depends(get_learning_service)
):
    """
    Get a specific question by ID
    """
    question = await learning_service.get_question_by_id(question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    return question


@router.post("/practice", response_model=PracticeSessionSchema)
async def create_practice_session(
    session_request: PracticeSessionCreateSchema,
    learning_service: LearningService = Depends(get_learning_service)
):
    """
    Create a new practice session with questions matching the requested criteria
    """
    try:
        session = await learning_service.create_practice_session(
            topic_ids=session_request.topic_ids,
            question_count=session_request.question_count,
            difficulty_range=session_request.difficulty_range
        )
        return session
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{question_id}/answer")
async def submit_answer(
    question_id: str = Path(..., description="The ID of the question being answered"),
    answer: QuestionAnswerSchema = None,
    learning_service: LearningService = Depends(get_learning_service)
):
    """
    Submit an answer to a question and receive feedback
    """
    if not answer:
        raise HTTPException(status_code=400, detail="Answer is required")
    
    try:
        result = await learning_service.check_answer(
            question_id=question_id,
            student_answer=answer.answer,
            time_taken_seconds=answer.time_taken_seconds
        )
        
        return JSONResponse(content={
            "correct": result["correct"],
            "correct_answer": result["correct_answer"],
            "explanation": result["explanation"]
        })
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")