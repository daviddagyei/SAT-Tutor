"""
SQLAlchemy implementation of the Question repository
"""
import random
from typing import Optional, List, Dict, Any, Tuple
from sqlalchemy import func, or_  # type: ignore
from sqlalchemy.orm import Session  # type: ignore

from ...models.question import Question, QuestionType
from ...repositories.question_repository import QuestionRepository
from ..database.models import QuestionModel
from .sqlalchemy_base_repository import SQLAlchemyRepository


class SQLAlchemyQuestionRepository(SQLAlchemyRepository[Question, QuestionModel], QuestionRepository):
    """
    SQLAlchemy implementation of the Question repository
    """
    
    def __init__(self, session: Session):
        """
        Initialize the repository with session
        
        Args:
            session: SQLAlchemy session
        """
        super().__init__(session, QuestionModel, Question)
    
    def get_by_topic(self, topic_id: str, difficulty: Optional[int] = None, 
                   count: int = 10) -> List[Question]:
        """
        Get questions for a specific topic with optional difficulty filter
        
        Args:
            topic_id: The ID of the topic
            difficulty: Optional difficulty level filter
            count: Maximum number of questions to return
            
        Returns:
            List of questions matching criteria
        """
        query = self.session.query(QuestionModel).filter(QuestionModel.topic_id == topic_id)
        
        if difficulty is not None:
            query = query.filter(QuestionModel.difficulty == difficulty)
            
        question_models = query.limit(count).all()
        return [self._to_domain(model) for model in question_models]
    
    def get_random_questions(self, subject_ids: List[str] = None, topic_ids: List[str] = None,
                           count: int = 10, difficulty_range: Tuple[int, int] = (1, 5),
                           question_type: Optional[QuestionType] = None) -> List[Question]:
        """
        Get random questions based on criteria
        
        Args:
            subject_ids: Optional list of subject IDs to include
            topic_ids: Optional list of topic IDs to include
            count: Number of questions to return
            difficulty_range: Range of difficulty levels (min, max)
            question_type: Optional specific question type
            
        Returns:
            List of random questions matching criteria
        """
        query = self.session.query(QuestionModel)
        
        # Apply filters
        if topic_ids:
            query = query.filter(QuestionModel.topic_id.in_(topic_ids))
            
        min_difficulty, max_difficulty = difficulty_range
        query = query.filter(QuestionModel.difficulty.between(min_difficulty, max_difficulty))
        
        if question_type:
            query = query.filter(QuestionModel.question_type == question_type)
        
        # Get all matching questions
        matching_questions = query.all()
        
        # If we have more than count, randomly sample count questions
        if len(matching_questions) > count:
            return [self._to_domain(q) for q in random.sample(matching_questions, count)]
        
        # Otherwise return all matching questions
        return [self._to_domain(q) for q in matching_questions]
    
    def get_questions_by_tags(self, tags: List[str], count: int = 10) -> List[Question]:
        """
        Get questions with specific tags
        
        Args:
            tags: List of tags to filter by
            count: Maximum number of questions to return
            
        Returns:
            List of questions with the specified tags
        """
        # This is a simplified implementation because JSONB queries are complex
        # In a real production app, we'd use PostgreSQL's JSONB operators for efficient querying
        # For now, we'll fetch questions and filter in Python
        questions = self.session.query(QuestionModel).all()
        
        # Filter questions that have any of the requested tags
        matching_questions = []
        for question in questions:
            if any(tag in question.tags for tag in tags):
                matching_questions.append(question)
                if len(matching_questions) >= count:
                    break
                    
        return [self._to_domain(q) for q in matching_questions]
    
    def get_total_by_topic(self, topic_id: str) -> int:
        """
        Count total questions for a specific topic
        
        Args:
            topic_id: The ID of the topic
            
        Returns:
            Number of questions for the topic
        """
        return self.session.query(func.count(QuestionModel.id)).filter(
            QuestionModel.topic_id == topic_id
        ).scalar()
    
    def get_total_by_difficulty(self, difficulty: int) -> int:
        """
        Count total questions with a specific difficulty level
        
        Args:
            difficulty: Difficulty level
            
        Returns:
            Number of questions with the specified difficulty
        """
        return self.session.query(func.count(QuestionModel.id)).filter(
            QuestionModel.difficulty == difficulty
        ).scalar()
    
    def update_question_difficulty(self, question_id: str, new_difficulty: int) -> bool:
        """
        Update a question's difficulty rating
        
        Args:
            question_id: ID of the question
            new_difficulty: New difficulty rating
            
        Returns:
            True if updated successfully, False otherwise
        """
        if not 1 <= new_difficulty <= 5:
            raise ValueError("Difficulty must be between 1 and 5")
            
        db_question = self.session.query(QuestionModel).get(question_id)
        if not db_question:
            return False
            
        db_question.difficulty = new_difficulty
        self.session.commit()
        
        return True
    
    def _to_domain(self, db_obj: QuestionModel) -> Question:
        """
        Convert a database question to a domain question
        
        Args:
            db_obj: Database question model instance
            
        Returns:
            Domain question entity
        """
        return Question(
            topic_id=db_obj.topic_id,
            question_type=db_obj.question_type,
            content=db_obj.content,
            answer=db_obj.answer,
            explanation=db_obj.explanation,
            difficulty=db_obj.difficulty,
            options=db_obj.options,
            tags=db_obj.tags,
            id=db_obj.id,
            created_at=db_obj.created_at,
            updated_at=db_obj.updated_at
        )
    
    def _to_db_obj(self, entity: Question) -> QuestionModel:
        """
        Convert a domain question to a database question
        
        Args:
            entity: Domain question entity
            
        Returns:
            Database question model instance
        """
        return QuestionModel(
            id=entity.id,
            topic_id=entity.topic_id,
            question_type=entity.question_type,
            content=entity.content,
            answer=entity.answer,
            explanation=entity.explanation,
            difficulty=entity.difficulty,
            options=entity.options,
            tags=entity.tags,
            created_at=entity.created_at,
            updated_at=entity.updated_at
        )
    
    def _update_db_obj(self, db_obj: QuestionModel, entity: Question) -> None:
        """
        Update a database question from a domain question
        
        Args:
            db_obj: Database question model instance to update
            entity: Domain question entity with updated values
        """
        db_obj.topic_id = entity.topic_id
        db_obj.question_type = entity.question_type
        db_obj.content = entity.content
        db_obj.answer = entity.answer
        db_obj.explanation = entity.explanation
        db_obj.difficulty = entity.difficulty
        db_obj.options = entity.options
        db_obj.tags = entity.tags
        db_obj.updated_at = entity.updated_at