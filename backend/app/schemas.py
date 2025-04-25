from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from .models import DifficultyLevel, ProcessingStatus

# User schemas
class UserBase(BaseModel):
    username: str
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    bio: Optional[str] = None
    profile_picture_url: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    bio: Optional[str] = None
    profile_picture_url: Optional[str] = None
    is_active: Optional[bool] = None

class UserInDB(UserBase):
    user_id: int
    created_at: datetime
    last_login: Optional[datetime] = None
    is_active: bool
    is_admin: bool

    class Config:
        orm_mode = True

class User(UserInDB):
    pass

# Problem schemas
class ProblemBase(BaseModel):
    title: str
    description: str
    difficulty: DifficultyLevel
    category: str
    estimated_time: Optional[int] = None
    is_active: bool = True

class ProblemCreate(ProblemBase):
    pass

class ProblemUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    difficulty: Optional[DifficultyLevel] = None
    category: Optional[str] = None
    estimated_time: Optional[int] = None
    is_active: Optional[bool] = None

class ProblemInDB(ProblemBase):
    problem_id: int
    created_at: datetime
    updated_at: datetime
    author_id: int

    class Config:
        orm_mode = True

class Problem(ProblemInDB):
    pass

# ProblemExample schemas
class ProblemExampleBase(BaseModel):
    example_text: str
    example_answer: str

class ProblemExampleCreate(ProblemExampleBase):
    problem_id: int

class ProblemExampleInDB(ProblemExampleBase):
    example_id: int
    problem_id: int
    created_at: datetime

    class Config:
        orm_mode = True

class ProblemExample(ProblemExampleInDB):
    pass

# Submission schemas
class SubmissionBase(BaseModel):
    answer_text: str
    audio_recording_url: Optional[str] = None

class SubmissionCreate(SubmissionBase):
    problem_id: int

class SubmissionUpdate(BaseModel):
    processing_status: Optional[ProcessingStatus] = None

class SubmissionInDB(SubmissionBase):
    submission_id: int
    user_id: int
    problem_id: int
    submission_time: datetime
    processing_status: ProcessingStatus

    class Config:
        orm_mode = True

class Submission(SubmissionInDB):
    pass

# Solution schema for the submit endpoint
class SolutionCreate(BaseModel):
    solution: str

# AIFeedback schemas
class AIFeedbackBase(BaseModel):
    overall_score: float = Field(..., ge=0, le=10)
    feedback_text: str
    structure_score: Optional[float] = Field(None, ge=0, le=10)
    clarity_score: Optional[float] = Field(None, ge=0, le=10)
    creativity_score: Optional[float] = Field(None, ge=0, le=10)
    confidence_score: Optional[float] = Field(None, ge=0, le=10)
    model_version: Optional[str] = None

class AIFeedbackCreate(AIFeedbackBase):
    submission_id: int

class AIFeedbackInDB(AIFeedbackBase):
    feedback_id: int
    submission_id: int
    generated_at: datetime

    class Config:
        orm_mode = True

class AIFeedback(AIFeedbackInDB):
    pass 