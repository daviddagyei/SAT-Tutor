"""
Practice session model for tracking user practice activities
"""
from datetime import datetime, UTC
from typing import List, Dict, Any, Optional

from .base import BaseModel


class PracticeSession(BaseModel):
    """
    PracticeSession entity representing a user's practice activity
    """
    
    def __init__(
        self,
        user_id: str,
        topic_ids: List[str],
        question_ids: List[str],
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        completed: bool = False,
        user_answers: Optional[List[Dict[str, Any]]] = None,
        score: Optional[float] = None,
        **kwargs
    ):
        """
        Initialize a new practice session
        
        Args:
            user_id: ID of the user taking the practice
            topic_ids: List of topic IDs covered in this session
            question_ids: List of question IDs included in this session
            start_time: When the session started
            end_time: When the session ended (None if ongoing)
            completed: Whether the session is complete
            user_answers: List of user answers with question_id, answer_given, is_correct
            score: Overall score for the session (percentage correct)
        """
        super().__init__(**kwargs)
        self.user_id = user_id
        self.topic_ids = topic_ids
        self.question_ids = question_ids
        self.start_time = start_time or datetime.now(UTC)
        self.end_time = end_time
        self.completed = completed
        self.user_answers = user_answers or []
        self.score = score
    
    def add_answer(self, question_id: str, answer_given: str, is_correct: bool, 
                 time_taken_seconds: int) -> None:
        """
        Add a user answer to the session
        
        Args:
            question_id: ID of the answered question
            answer_given: User's answer
            is_correct: Whether the answer is correct
            time_taken_seconds: Time taken to answer in seconds
        """
        self.user_answers.append({
            "question_id": question_id,
            "answer_given": answer_given,
            "is_correct": is_correct,
            "time_taken_seconds": time_taken_seconds,
            "timestamp": datetime.now(UTC).isoformat()
        })
        self.update()
    
    def complete_session(self) -> None:
        """
        Mark the session as completed and calculate the final score
        """
        self.completed = True
        self.end_time = datetime.now(UTC)
        
        # Calculate score as percentage of correct answers
        if self.user_answers:
            correct_answers = sum(1 for answer in self.user_answers if answer.get("is_correct", False))
            self.score = (correct_answers / len(self.user_answers)) * 100
        else:
            self.score = 0
            
        self.update()
    
    def get_duration_minutes(self) -> Optional[float]:
        """
        Calculate the session duration in minutes
        
        Returns:
            Duration in minutes or None if session is ongoing
        """
        if not self.end_time:
            return None
            
        delta = self.end_time - self.start_time
        return delta.total_seconds() / 60
    
    def get_topic_performance(self) -> Dict[str, Dict[str, Any]]:
        """
        Calculate performance metrics grouped by topic
        
        Returns:
            Dictionary with topic IDs as keys and performance data as values
        """
        topic_performance = {}
        
        # Initialize performance data for each topic
        for topic_id in self.topic_ids:
            topic_performance[topic_id] = {
                "correct": 0,
                "total": 0,
                "avg_time": 0,
                "questions": []
            }
        
        # Group question data by topic
        for answer in self.user_answers:
            # In a real implementation, we would need to look up the topic for each question
            # For simplicity, we'll just use the first topic for all questions
            topic_id = self.topic_ids[0] if self.topic_ids else "unknown"
            
            if topic_id in topic_performance:
                topic_performance[topic_id]["total"] += 1
                if answer.get("is_correct", False):
                    topic_performance[topic_id]["correct"] += 1
                    
                topic_performance[topic_id]["questions"].append(answer)
                
                # Update average time
                total_time = topic_performance[topic_id]["avg_time"] * (topic_performance[topic_id]["total"] - 1)
                total_time += answer.get("time_taken_seconds", 0)
                topic_performance[topic_id]["avg_time"] = total_time / topic_performance[topic_id]["total"]
        
        # Calculate percentages
        for topic_id, data in topic_performance.items():
            if data["total"] > 0:
                data["percentage"] = (data["correct"] / data["total"]) * 100
            else:
                data["percentage"] = 0
        
        return topic_performance