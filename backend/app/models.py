from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Enum, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import enum
from datetime import datetime

Base = declarative_base()

class DifficultyLevel(str, enum.Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    EXPERT = "expert"

class ProcessingStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    first_name = Column(String)
    last_name = Column(String)
    profile_picture_url = Column(String)
    bio = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)

    # Relationships
    problems = relationship("Problem", back_populates="author")
    submissions = relationship("Submission", back_populates="user")

class Problem(Base):
    __tablename__ = "problems"

    problem_id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    difficulty = Column(Enum(DifficultyLevel), nullable=False)
    category = Column(String, nullable=False)
    estimated_time = Column(Integer)  # Time in minutes
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    author_id = Column(Integer, ForeignKey("users.user_id"))

    # Relationships
    author = relationship("User", back_populates="problems")
    examples = relationship("ProblemExample", back_populates="problem")
    submissions = relationship("Submission", back_populates="problem")

class ProblemExample(Base):
    __tablename__ = "problem_examples"

    example_id = Column(Integer, primary_key=True, index=True)
    problem_id = Column(Integer, ForeignKey("problems.problem_id"))
    example_text = Column(Text, nullable=False)
    example_answer = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    problem = relationship("Problem", back_populates="examples")

class Submission(Base):
    __tablename__ = "submissions"

    submission_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    problem_id = Column(Integer, ForeignKey("problems.problem_id"))
    answer_text = Column(Text, nullable=False)
    audio_recording_url = Column(String)
    submission_time = Column(DateTime, default=datetime.utcnow)
    processing_status = Column(Enum(ProcessingStatus), default=ProcessingStatus.PENDING)

    # Relationships
    user = relationship("User", back_populates="submissions")
    problem = relationship("Problem", back_populates="submissions")
    feedback = relationship("AIFeedback", back_populates="submission", uselist=False)

class AIFeedback(Base):
    __tablename__ = "ai_feedback"

    feedback_id = Column(Integer, primary_key=True, index=True)
    submission_id = Column(Integer, ForeignKey("submissions.submission_id"), unique=True)
    overall_score = Column(Float, nullable=False)  # 1-10
    feedback_text = Column(Text, nullable=False)
    structure_score = Column(Float)  # 1-5
    clarity_score = Column(Float)  # 1-5
    creativity_score = Column(Float)  # 1-5
    confidence_score = Column(Float)  # 1-5
    generated_at = Column(DateTime, default=datetime.utcnow)
    model_version = Column(String)

    # Relationships
    submission = relationship("Submission", back_populates="feedback") 