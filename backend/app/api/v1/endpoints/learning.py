"""
Learning API endpoints for practice sessions and questions
"""
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status  # type: ignore
from pydantic import BaseModel, Field  # type: ignore

from ....services.learning_service import LearningService
from ....models.question import Question, QuestionType
from ....models.practice_session import PracticeSession
from ....models.user import User
from ...deps import get_learning_service, get_current_active_user

router = APIRouter()

# Schema models
class QuestionResponse(BaseModel):
    """Schema for question response"""
    id: str
    topic_id: str
    question_type: str
    content: str
    options: Optional[List[Dict[str, Any]]] = None
    difficulty: int
    tags: List[str]

class QuestionListResponse(BaseModel):
    """Schema for list of questions response"""
    questions: List[QuestionResponse]
    total: int

class SessionCreate(BaseModel):
    """Schema for creating a practice session"""
    topic_ids: Optional[List[str]] = None
    question_count: int = Field(default=10, ge=1, le=50)
    difficulty_min: int = Field(default=1, ge=1, le=5)
    difficulty_max: int = Field(default=5, ge=1, le=5)

class AnswerSubmit(BaseModel):
    """Schema for submitting an answer"""
    session_id: str
    question_id: str
    answer: str
    time_taken_seconds: int = Field(ge=1)

class AnswerResponse(BaseModel):
    """Schema for answer response"""
    is_correct: bool
    correct_answer: str
    explanation: str

class SessionSummary(BaseModel):
    """Schema for session summary"""
    session_id: str
    score: float
    duration_minutes: Optional[float]
    questions_answered: int
    correct_answers: int
    topic_performance: Dict[str, Any]

@router.get("/questions/personalized", response_model=QuestionListResponse)
async def get_personalized_questions(
    count: int = 10,
    current_user: User = Depends(get_current_active_user),
    learning_service: LearningService = Depends(get_learning_service)
):
    """
    Get personalized practice questions for the current user
    """
    questions = learning_service.get_personalized_questions(
        user_id=current_user.id, 
        count=count
    )
    
    # Convert Questions to QuestionResponse objects
    questions_response = [
        QuestionResponse(
            id=q.id,
            topic_id=q.topic_id,
            question_type=q.question_type.value,
            content=q.content,
            options=q.options,
            difficulty=q.difficulty,
            tags=q.tags
        ) 
        for q in questions
    ]
    
    return {
        "questions": questions_response,
        "total": len(questions_response)
    }

@router.post("/sessions", response_model=Dict[str, str])
async def create_practice_session(
    session_data: SessionCreate,
    current_user: User = Depends(get_current_active_user),
    learning_service: LearningService = Depends(get_learning_service)
):
    """
    Create a new practice session for the current user
    """
    session = learning_service.create_practice_session(
        user_id=current_user.id,
        topic_ids=session_data.topic_ids,
        question_count=session_data.question_count,
        difficulty_range=(session_data.difficulty_min, session_data.difficulty_max)
    )
    
    return {
        "session_id": session.id,
        "message": "Practice session created successfully",
        "question_count": len(session.question_ids)
    }

@router.post("/sessions/answers", response_model=AnswerResponse)
async def submit_answer(
    answer_data: AnswerSubmit,
    current_user: User = Depends(get_current_active_user),
    learning_service: LearningService = Depends(get_learning_service)
):
    """
    Submit an answer to a question in a practice session
    """
    # In a complete implementation, we would retrieve the session from a repository
    # For this example, we'll create a mock session
    session = PracticeSession(
        user_id=current_user.id,
        topic_ids=["topic1"],
        question_ids=[answer_data.question_id]
    )
    
    try:
        result = learning_service.submit_answer(
            session=session,
            question_id=answer_data.question_id,
            answer=answer_data.answer,
            time_taken_seconds=answer_data.time_taken_seconds
        )
        
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/sessions/{session_id}/complete", response_model=SessionSummary)
async def complete_session(
    session_id: str,
    current_user: User = Depends(get_current_active_user),
    learning_service: LearningService = Depends(get_learning_service)
):
    """
    Complete a practice session and get results
    """
    # In a complete implementation, we would retrieve the session from a repository
    # For this example, we'll create a mock session
    session = PracticeSession(
        id=session_id,
        user_id=current_user.id,
        topic_ids=["topic1"],
        question_ids=["question1", "question2"]
    )
    
    # Add some mock answers for demonstration
    session.add_answer("question1", "A", True, 30)
    session.add_answer("question2", "B", False, 45)
    
    result = learning_service.complete_practice_session(session)
    
    return result

@router.get("/topics/mastery/{topic_id}", response_model=Dict[str, float])
async def get_topic_mastery(
    topic_id: str,
    current_user: User = Depends(get_current_active_user),
    learning_service: LearningService = Depends(get_learning_service)
):
    """
    Get the user's mastery percentage for a specific topic
    """
    mastery = learning_service.calculate_topic_mastery(
        user_id=current_user.id,
        topic_id=topic_id
    )
    
    return {"mastery_percentage": mastery}

@router.get("/questions/{question_id}/hint", response_model=Dict[str, str])
async def get_question_hint(
    question_id: str,
    current_user: User = Depends(get_current_active_user),
    learning_service: LearningService = Depends(get_learning_service)
):
    """
    Get a hint for a specific question
    """
    try:
        hint = learning_service.get_hint(question_id)
        return {"hint": hint}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )