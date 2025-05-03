"""
Profile model for extended user information related to learning
"""
from datetime import datetime
from typing import Dict, List, Any, Optional

from .base import BaseModel


class Profile(BaseModel):
    """
    Extended user profile with achievements and learning data
    """
    
    def __init__(
        self,
        user_id: str,
        bio: str = "",
        study_goals: Optional[Dict[str, Any]] = None,
        achievements: Optional[List[Dict[str, Any]]] = None,
        study_streak: int = 0,
        last_activity_date: Optional[datetime] = None,
        sat_target_score: Optional[int] = None,
        current_estimated_score: Optional[Dict[str, int]] = None,
        **kwargs
    ):
        """
        Initialize a new user profile
        
        Args:
            user_id: ID of the associated user
            bio: User's biography/description
            study_goals: Dictionary of study goals and targets
            achievements: List of user achievements
            study_streak: Number of consecutive study days
            last_activity_date: Date of last learning activity
            sat_target_score: User's target SAT score
            current_estimated_score: Current estimated scores by section
        """
        super().__init__(**kwargs)
        self.user_id = user_id
        self.bio = bio
        self.study_goals = study_goals or {}
        self.achievements = achievements or []
        self.study_streak = study_streak
        self.last_activity_date = last_activity_date or datetime.utcnow()
        self.sat_target_score = sat_target_score
        self.current_estimated_score = current_estimated_score or {"math": 0, "verbal": 0}
    
    def record_activity(self) -> None:
        """
        Record a learning activity, updating streak and last activity date
        """
        today = datetime.utcnow().date()
        last_date = self.last_activity_date.date() if self.last_activity_date else None
        
        # If first activity or activity on a new day (not same as last activity)
        if not last_date or today > last_date:
            # Check if the last activity was yesterday to maintain streak
            if last_date and (today - last_date).days == 1:
                self.study_streak += 1
            # If more than 1 day has passed, reset streak
            elif last_date and (today - last_date).days > 1:
                self.study_streak = 1
            # First ever activity
            elif not last_date:
                self.study_streak = 1
                
        self.last_activity_date = datetime.utcnow()
        self.update()
    
    def add_achievement(self, achievement: Dict[str, Any]) -> None:
        """
        Add a new achievement to the profile
        
        Args:
            achievement: Achievement data including name, description, and date
        """
        if not achievement.get('date'):
            achievement['date'] = datetime.utcnow().isoformat()
            
        self.achievements.append(achievement)
        self.update()
    
    def update_estimated_score(self, section: str, score: int) -> None:
        """
        Update the current estimated score for a section
        
        Args:
            section: Section name (math, verbal)
            score: New estimated score
        """
        if section not in self.current_estimated_score:
            raise ValueError(f"Invalid section: {section}")
            
        self.current_estimated_score[section] = score
        self.update()
    
    def set_target_score(self, score: int) -> None:
        """
        Set the user's target SAT score
        
        Args:
            score: Target total SAT score
        """
        self.sat_target_score = score
        self.update()