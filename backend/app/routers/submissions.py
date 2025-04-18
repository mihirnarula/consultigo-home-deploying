from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .. import models, schemas, database
from typing import List

router = APIRouter(
    prefix="/submissions",
    tags=["submissions"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=schemas.Submission, status_code=status.HTTP_201_CREATED)
def create_submission(submission: schemas.SubmissionCreate, user_id: int, db: Session = Depends(database.get_db)):
    # Check if user exists
    user = db.query(models.User).filter(models.User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if problem exists
    problem = db.query(models.Problem).filter(models.Problem.problem_id == submission.problem_id).first()
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")
    
    # Create submission
    db_submission = models.Submission(
        user_id=user_id,
        problem_id=submission.problem_id,
        answer_text=submission.answer_text,
        audio_recording_url=submission.audio_recording_url,
        processing_status=models.ProcessingStatus.PENDING
    )
    db.add(db_submission)
    db.commit()
    db.refresh(db_submission)
    return db_submission

@router.get("/", response_model=List[schemas.Submission])
def read_submissions(skip: int = 0, limit: int = 100, user_id: int = None, problem_id: int = None, 
                   db: Session = Depends(database.get_db)):
    query = db.query(models.Submission)
    
    if user_id:
        query = query.filter(models.Submission.user_id == user_id)
    
    if problem_id:
        query = query.filter(models.Submission.problem_id == problem_id)
    
    submissions = query.offset(skip).limit(limit).all()
    return submissions

@router.get("/{submission_id}", response_model=schemas.Submission)
def read_submission(submission_id: int, db: Session = Depends(database.get_db)):
    db_submission = db.query(models.Submission).filter(models.Submission.submission_id == submission_id).first()
    if db_submission is None:
        raise HTTPException(status_code=404, detail="Submission not found")
    return db_submission

@router.put("/{submission_id}", response_model=schemas.Submission)
def update_submission(submission_id: int, submission: schemas.SubmissionUpdate, db: Session = Depends(database.get_db)):
    db_submission = db.query(models.Submission).filter(models.Submission.submission_id == submission_id).first()
    if db_submission is None:
        raise HTTPException(status_code=404, detail="Submission not found")
    
    update_data = submission.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_submission, key, value)
    
    db.commit()
    db.refresh(db_submission)
    return db_submission

# AI Feedback endpoints
@router.post("/{submission_id}/feedback", response_model=schemas.AIFeedback, status_code=status.HTTP_201_CREATED)
def create_ai_feedback(submission_id: int, feedback: schemas.AIFeedbackBase, db: Session = Depends(database.get_db)):
    # Check if submission exists
    db_submission = db.query(models.Submission).filter(models.Submission.submission_id == submission_id).first()
    if db_submission is None:
        raise HTTPException(status_code=404, detail="Submission not found")
    
    # Check if feedback already exists
    existing_feedback = db.query(models.AIFeedback).filter(models.AIFeedback.submission_id == submission_id).first()
    if existing_feedback:
        raise HTTPException(status_code=400, detail="Feedback for this submission already exists")
    
    # Create feedback
    db_feedback = models.AIFeedback(
        submission_id=submission_id,
        overall_score=feedback.overall_score,
        feedback_text=feedback.feedback_text,
        structure_score=feedback.structure_score,
        clarity_score=feedback.clarity_score,
        creativity_score=feedback.creativity_score,
        confidence_score=feedback.confidence_score,
        model_version=feedback.model_version
    )
    db.add(db_feedback)
    db.commit()
    db.refresh(db_feedback)
    
    # Update submission status
    db_submission.processing_status = models.ProcessingStatus.COMPLETED
    db.commit()
    
    return db_feedback

@router.get("/{submission_id}/feedback", response_model=schemas.AIFeedback)
def read_ai_feedback(submission_id: int, db: Session = Depends(database.get_db)):
    # Check if submission exists
    db_submission = db.query(models.Submission).filter(models.Submission.submission_id == submission_id).first()
    if db_submission is None:
        raise HTTPException(status_code=404, detail="Submission not found")
    
    feedback = db.query(models.AIFeedback).filter(models.AIFeedback.submission_id == submission_id).first()
    if feedback is None:
        raise HTTPException(status_code=404, detail="Feedback not found for this submission")
    
    return feedback 