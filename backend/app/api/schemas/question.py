"""
Pydantic schemas for question-related API endpoints
"""
from typing import List, Dict, Optional, Any, Union
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum

class QuestionTypeEnum(str, Enum):
    MULTIPLE_CHOICE = "multiple_choice"
    ESSAY = "essay"
    SHORT_ANSWER = "short_answer"
    FILL_IN_BLANK = "fill_in_blank"


class AnswerOptionSchema(BaseModel):
    id: str
    text: str
    image_url: Optional[str] = None
    is_correct: Optional[bool] = None  # Only exposed for correct answers


class QuestionSchema(BaseModel):
    id: str
    text: str
    difficulty: int = Field(..., ge=1, le=5)
    question_type: str
    topic_id: str
    topic_name: Optional[str] = None
    subject_id: Optional[str] = None
    subject_name: Optional[str] = None
    tags: List[str] = []
    image_url: Optional[str] = None


class QuestionDetailSchema(QuestionSchema):
    answer_options: Optional[List[AnswerOptionSchema]] = None
    explanation: Optional[str] = None
    solution_steps: Optional[List[str]] = None
    related_concepts: Optional[List[str]] = None
    correct_answer: Optional[Union[str, List[str]]] = None  # For non-multiple choice questions


class PracticeSessionCreateSchema(BaseModel):
    topic_ids: List[str]
    question_count: int = Field(10, ge=1, le=50)
    difficulty_range: Optional[List[int]] = Field(default=[1, 5])


class PracticeSessionQuestionSchema(BaseModel):
    id: str
    question_id: str
    question: QuestionSchema
    answered: bool = False
    correct: Optional[bool] = None
    time_taken_seconds: Optional[int] = None


class PracticeSessionSchema(BaseModel):
    id: str
    user_id: Optional[str] = None
    start_time: datetime
    end_time: Optional[datetime] = None
    questions: List[PracticeSessionQuestionSchema] = []
    completed: bool = False
    score: Optional[int] = None


class QuestionAnswerSchema(BaseModel):
    answer: Union[str, List[str]]  # Could be a single answer or multiple selections
    time_taken_seconds: Optional[int] = None
    confidence_level: Optional[int] = Field(None, ge=1, le=5)