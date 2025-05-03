"""
Learning service for practice sessions and questions
"""
import random
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple

from ..models.question import Question
from ..models.practice_session import PracticeSession
from ..models.topic import Topic
from ..repositories.question_repository import QuestionRepository
from ..repositories.user_repository import UserRepository


class LearningService:
    """
    Service for learning functionality including practice sessions,
    questions, and personalized recommendations
    """
    
    def __init__(self, question_repository: QuestionRepository, user_repository: UserRepository):
        """
        Initialize the learning service
        
        Args:
            question_repository: Repository for question data access
            user_repository: Repository for user data access
        """
        self.question_repository = question_repository
        self.user_repository = user_repository
    
    def get_recommended_topics(self, user_id: str, count: int = 3) -> List[str]:
        """
        Get topic IDs recommended for a user based on their performance history
        
        Args:
            user_id: ID of the user
            count: Number of topics to recommend
            
        Returns:
            List of recommended topic IDs
        """
        # In a real implementation, this would use analytics data to make smart recommendations
        # For this example, we'll just return some placeholder logic
        
        # Get topics the user has practiced recently (mock implementation)
        recent_topics = ["topic1", "topic2", "topic3"]
        
        # Get topics where performance is below threshold (mock implementation)
        struggling_topics = ["topic4", "topic5"]
        
        # Prioritize struggling topics, then add others
        recommendations = struggling_topics.copy()
        
        # Add more topics if needed to reach count
        for topic in recent_topics:
            if topic not in recommendations:
                recommendations.append(topic)
                if len(recommendations) >= count:
                    break
        
        return recommendations[:count]
    
    def get_personalized_questions(self, user_id: str, count: int = 10) -> List[Question]:
        """
        Get personalized practice questions for a user
        
        Args:
            user_id: ID of the user
            count: Number of questions to return
            
        Returns:
            List of personalized questions
        """
        # Get recommended topics
        topic_ids = self.get_recommended_topics(user_id)
        
        # Get questions for those topics
        questions = self.question_repository.get_random_questions(
            topic_ids=topic_ids,
            count=count
        )
        
        return questions
    
    def create_practice_session(self, user_id: str, topic_ids: List[str] = None,
                              question_count: int = 10, difficulty_range: Tuple[int, int] = (1, 5)) -> PracticeSession:
        """
        Create a new practice session for a user
        
        Args:
            user_id: ID of the user
            topic_ids: Optional list of topic IDs to focus on
            question_count: Number of questions to include
            difficulty_range: Range of difficulty levels (min, max)
            
        Returns:
            New practice session with questions
        """
        # If no topics provided, use recommended topics
        if not topic_ids:
            topic_ids = self.get_recommended_topics(user_id)
            
        # Get random questions for the session
        questions = self.question_repository.get_random_questions(
            topic_ids=topic_ids,
            count=question_count,
            difficulty_range=difficulty_range
        )
        
        # Extract question IDs
        question_ids = [q.id for q in questions]
        
        # Create a new practice session
        session = PracticeSession(
            user_id=user_id,
            topic_ids=topic_ids,
            question_ids=question_ids
        )
        
        return session
    
    def submit_answer(self, session: PracticeSession, question_id: str, 
                    answer: str, time_taken_seconds: int) -> Dict[str, Any]:
        """
        Submit a user's answer to a question in a practice session
        
        Args:
            session: The practice session
            question_id: ID of the question being answered
            answer: User's answer
            time_taken_seconds: Time taken in seconds
            
        Returns:
            Result with correctness, explanation, etc.
        """
        # Validate that the question is part of the session
        if question_id not in session.question_ids:
            raise ValueError(f"Question {question_id} is not part of this session")
            
        # Get the question
        question = self.question_repository.get_by_id(question_id)
        if not question:
            raise ValueError(f"Question {question_id} not found")
            
        # Check if the answer is correct
        is_correct = question.is_correct_answer(answer)
        
        # Add the answer to the session
        session.add_answer(question_id, answer, is_correct, time_taken_seconds)
        
        # Return the result
        return {
            "is_correct": is_correct,
            "correct_answer": question.answer,
            "explanation": question.explanation
        }
    
    def complete_practice_session(self, session: PracticeSession) -> Dict[str, Any]:
        """
        Complete a practice session and calculate results
        
        Args:
            session: The practice session to complete
            
        Returns:
            Session summary with score and analytics
        """
        # Mark the session as completed
        session.complete_session()
        
        # Calculate topic performance metrics
        topic_performance = session.get_topic_performance()
        
        # Return summary
        return {
            "session_id": session.id,
            "score": session.score,
            "duration_minutes": session.get_duration_minutes(),
            "questions_answered": len(session.user_answers),
            "correct_answers": sum(1 for a in session.user_answers if a.get("is_correct", False)),
            "topic_performance": topic_performance
        }
    
    def calculate_topic_mastery(self, user_id: str, topic_id: str) -> float:
        """
        Calculate a user's mastery percentage for a specific topic
        
        Args:
            user_id: ID of the user
            topic_id: ID of the topic
            
        Returns:
            Mastery percentage (0-100)
        """
        # In a real implementation, this would analyze all practice session data
        # For this example, we'll return a mock calculation
        
        # Mock implementation
        # This would typically involve analyzing past sessions for this topic
        return random.uniform(50, 95)
    
    def get_hint(self, question_id: str) -> str:
        """
        Get a hint for a specific question
        
        Args:
            question_id: ID of the question
            
        Returns:
            Hint text
        """
        question = self.question_repository.get_by_id(question_id)
        if not question:
            raise ValueError(f"Question {question_id} not found")
            
        return question.get_hint()
        
    async def update_practice_progress(self, user_id: str, topic_id: str, completed: bool, correct: bool) -> Dict[str, Any]:
        """
        Update a user's progress after completing a practice question
        
        Args:
            user_id: ID of the user
            topic_id: ID of the topic
            completed: Whether the question was completed
            correct: Whether the answer was correct
            
        Returns:
            Updated progress information
        """
        try:
            # This would usually call the user_repository to update the progress in the database
            # For now, let's just return a success response
            
            # In a real implementation with Supabase, we would do something like:
            # await supabase.from('user_progress').upsert({
            #     user_id: user_id,
            #     topic_id: topic_id,
            #     completed_exercises: completed ? 1 : 0,
            #     correct_answers: correct ? 1 : 0,
            #     last_attempt_at: new Date().toISOString()
            # })
            
            return {
                "user_id": user_id,
                "topic_id": topic_id,
                "completed": completed,
                "correct": correct,
                "updated_at": datetime.utcnow().isoformat()
            }
        except Exception as e:
            raise ValueError(f"Failed to update progress: {str(e)}")