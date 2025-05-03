"""
SQLAlchemy models for database tables
"""
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional

from sqlalchemy import (  # type: ignore
    Column, String, Integer, Float, Boolean, 
    DateTime, ForeignKey, Text, Enum, JSON
)
from sqlalchemy.orm import relationship  # type: ignore

from .session import Base
from ...models.question import QuestionType
from ...models.user import UserRole


class UserModel(Base):
    """SQLAlchemy model for users table"""
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.STUDENT, nullable=False)
    profile_image_url = Column(String, nullable=True)
    is_email_confirmed = Column(Boolean, default=False, nullable=False)
    email_confirmation_token = Column(String, nullable=True, unique=True)
    password_reset_token = Column(String, nullable=True, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    profile = relationship("ProfileModel", back_populates="user", uselist=False)
    practice_sessions = relationship("PracticeSessionModel", back_populates="user")
    
    def __repr__(self):
        return f"<User {self.email}>"


class ProfileModel(Base):
    """SQLAlchemy model for user profiles table"""
    __tablename__ = "profiles"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    bio = Column(Text, nullable=True)
    study_goals = Column(JSON, default={}, nullable=False)
    achievements = Column(JSON, default=[], nullable=False)
    study_streak = Column(Integer, default=0, nullable=False)
    last_activity_date = Column(DateTime, default=datetime.utcnow, nullable=True)
    sat_target_score = Column(Integer, nullable=True)
    current_estimated_score = Column(JSON, default={"math": 0, "verbal": 0}, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("UserModel", back_populates="profile")
    
    def __repr__(self):
        return f"<Profile {self.user_id}>"


class SubjectModel(Base):
    """SQLAlchemy model for subjects table"""
    __tablename__ = "subjects"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, unique=True, nullable=False)
    description = Column(Text, nullable=False)
    icon = Column(String, default="book", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    topics = relationship("TopicModel", back_populates="subject")
    
    def __repr__(self):
        return f"<Subject {self.name}>"


class TopicModel(Base):
    """SQLAlchemy model for topics table"""
    __tablename__ = "topics"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    subject_id = Column(String, ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    difficulty_level = Column(Integer, default=1, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    subject = relationship("SubjectModel", back_populates="topics")
    questions = relationship("QuestionModel", back_populates="topic")
    
    def __repr__(self):
        return f"<Topic {self.name}>"


class QuestionModel(Base):
    """SQLAlchemy model for questions table"""
    __tablename__ = "questions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    topic_id = Column(String, ForeignKey("topics.id", ondelete="CASCADE"), nullable=False)
    question_type = Column(Enum(QuestionType), nullable=False)
    content = Column(Text, nullable=False)
    answer = Column(String, nullable=False)
    explanation = Column(Text, nullable=False)
    difficulty = Column(Integer, default=3, nullable=False)
    options = Column(JSON, nullable=True)  # For multiple choice questions
    tags = Column(JSON, default=[], nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    topic = relationship("TopicModel", back_populates="questions")
    
    def __repr__(self):
        return f"<Question {self.id[:8]}>"


class PracticeSessionModel(Base):
    """SQLAlchemy model for practice sessions table"""
    __tablename__ = "practice_sessions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    start_time = Column(DateTime, default=datetime.utcnow, nullable=False)
    end_time = Column(DateTime, nullable=True)
    completed = Column(Boolean, default=False, nullable=False)
    score = Column(Float, nullable=True)
    topic_ids = Column(JSON, default=[], nullable=False)
    question_ids = Column(JSON, default=[], nullable=False)
    user_answers = Column(JSON, default=[], nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("UserModel", back_populates="practice_sessions")
    
    def __repr__(self):
        return f"<PracticeSession {self.id[:8]}>"


class CourseModel(Base):
    """SQLAlchemy model for courses table"""
    __tablename__ = "courses"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    instructor_id = Column(String, ForeignKey("users.id"), nullable=False)
    subject_ids = Column(JSON, default=[], nullable=False)
    level = Column(String, nullable=False)  # beginner, intermediate, advanced
    thumbnail_url = Column(String, nullable=True)
    is_published = Column(Boolean, default=False, nullable=False)
    estimated_duration_hours = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    instructor = relationship("UserModel", foreign_keys=[instructor_id])
    sections = relationship("CourseSectionModel", back_populates="course", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Course {self.title}>"


class CourseSectionModel(Base):
    """SQLAlchemy model for course sections table"""
    __tablename__ = "course_sections"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    course_id = Column(String, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    order_index = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    course = relationship("CourseModel", back_populates="sections")
    lessons = relationship("LessonModel", back_populates="section", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<CourseSection {self.title}>"


class LessonModel(Base):
    """SQLAlchemy model for lessons table"""
    __tablename__ = "lessons"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    section_id = Column(String, ForeignKey("course_sections.id", ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    video_url = Column(String, nullable=True)
    order_index = Column(Integer, nullable=False)
    estimated_duration_minutes = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    section = relationship("CourseSectionModel", back_populates="lessons")
    
    def __repr__(self):
        return f"<Lesson {self.title}>"


class UserLessonProgressModel(Base):
    """SQLAlchemy model for tracking user lesson completion"""
    __tablename__ = "user_lesson_progress"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    lesson_id = Column(String, ForeignKey("lessons.id", ondelete="CASCADE"), nullable=False)
    completed = Column(Boolean, default=False, nullable=False)
    completion_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<UserLessonProgress {self.user_id}:{self.lesson_id}>"