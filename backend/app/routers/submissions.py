from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from .. import models, schemas, database, auth
from typing import List
import requests
import os
from dotenv import load_dotenv
import logging
from datetime import datetime
import json
import random
import re
import traceback
import time
from sqlalchemy import text

# Load environment variables (create a .env file later)
load_dotenv()

# Create a logger for this module
logger = logging.getLogger(__name__)

# Get the API key from environment variables or use the provided one
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyA6K4a744vr787q6qf8WIScqV70kIi23Lo")
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

# Helper function to generate mock feedback when API calls fail
def generate_mock_feedback(problem_title, problem_description, solution_text):
    """Generate mock feedback when the API call fails"""
    logger.warning("Using mock feedback generation as fallback")
    
    # Extract key information for the feedback
    problem_type = "case study" if "Case Study" in problem_description else "guesstimate"
    solution_length = len(solution_text)
    solution_paragraphs = solution_text.count('\n\n') + 1
    
    # Check if solution is too short or nonsensical
    required_keywords = ["market", "strategy", "business", "company", "customer", "product", "service", "analysis", "approach", "calculate", "estimate", "quantity", "number"]
    keyword_presence = [word for word in required_keywords if word in solution_text.lower()]
    
    # Stricter check for nonsensical submissions
    if solution_length < 100 or len(keyword_presence) < 2:
        # For bad responses, determine score based on length and keyword presence
        if solution_length < 50:
            overall_score = 1.5  # Very short gets very low score
        elif solution_length < 100:
            overall_score = 2.5  # Short but not extremely short
        else:
            overall_score = 3.0  # Longer but still poor quality
        
        structure_score = max(1.0, overall_score - 1.0)
        clarity_score = max(1.0, overall_score - 0.5)
        creativity_score = max(1.0, overall_score - 1.5)
        confidence_score = max(1.0, overall_score - 1.0)
        
        logger.info(f"Mock feedback using BAD score: {overall_score} for solution length {solution_length} with {len(keyword_presence)} relevant keywords")
        
        # Generate critical feedback that points out the deficiencies
        feedback = f"""# Feedback on {problem_title}

Score Summary:
Overall Score: {overall_score}/10
Structure: {structure_score}/10
{"Assumptions" if problem_type == "guesstimate" else "Assumptions Quality"}: {clarity_score}/10
{"Math Accuracy" if problem_type == "guesstimate" else "Analysis Quality"}: {creativity_score}/10
Communication: {confidence_score}/10

- Relevance: No - The response does not adequately address the key components of a {problem_type} solution.
- Strengths: None identified.
- Areas for improvement:
  * Provide a structured approach with clear steps and framework
  * Include relevant data points and quantitative analysis
  * Develop a comprehensive solution that addresses all aspects of the problem
  * {"Ensure calculations are accurate and logical" if problem_type == "guesstimate" else "Include market analysis and strategic recommendations"}
  * Improve clarity and organization of ideas
- Final Assessment: The response is insufficient and does not meet the minimum requirements for a consulting {problem_type} solution. Additional depth, structure, and analysis are needed.
"""
        return feedback
    
    # For adequate solutions, score based on length and quality indicators
    # More paragraphs and better keywords = higher score
    analysis_keywords = ["analysis", "segment", "target", "competitor", "revenue", "profit", "strategy", "implementation"]
    quantitative_keywords = ["calculate", "estimate", "number", "percent", "market size", "growth rate", "cost", "revenue"]
    
    analysis_keyword_count = sum(1 for keyword in analysis_keywords if keyword in solution_text.lower())
    quantitative_keyword_count = sum(1 for keyword in quantitative_keywords if keyword in solution_text.lower())
    
    # Base score on length, keyword richness, and structure
    if solution_length > 800 and analysis_keyword_count >= 4 and quantitative_keyword_count >= 3:
        overall_score = 8.0  # Longer with good keywords
        structure_score = 7.5
        clarity_score = 7.0
        creativity_score = 7.5
        confidence_score = 7.0
    elif solution_length > 500 and (analysis_keyword_count + quantitative_keyword_count) >= 4:
        overall_score = 7.0  # Medium length with decent keywords
        structure_score = 6.5
        clarity_score = 6.0
        creativity_score = 6.5
        confidence_score = 6.0
    elif solution_length > 300:
        overall_score = 6.0  # Shorter but still acceptable
        structure_score = 5.5
        clarity_score = 5.0
        creativity_score = 5.5
        confidence_score = 5.0
    else:
        overall_score = 5.0  # Minimal acceptable length
        structure_score = 4.5
        clarity_score = 4.0
        creativity_score = 4.5
        confidence_score = 4.0
    
    logger.info(f"Mock feedback using ACCEPTABLE score: {overall_score} for solution with length {solution_length}, " 
                f"{analysis_keyword_count} analysis keywords, and {quantitative_keyword_count} quantitative keywords")
    
    # Create feedback based on solution characteristics
    feedback = f"""# Feedback on {problem_title}

Score Summary:
Overall Score: {overall_score}/10
Structure: {structure_score}/10
{"Assumptions" if problem_type == "guesstimate" else "Assumptions Quality"}: {clarity_score}/10
{"Math Accuracy" if problem_type == "guesstimate" else "Analysis Quality"}: {creativity_score}/10
Communication: {confidence_score}/10

- Relevance: Yes - The response addresses the {problem_type} problem with appropriate analysis.
- Strengths:
  * Demonstrates understanding of the problem context
  * Uses a methodical approach to analyzing the situation
  * Includes specific insights relevant to the {problem_type} scenario
  * Organizes content with {solution_paragraphs} distinct sections
- Areas for improvement:
  * Include more detailed quantitative analysis to strengthen arguments
  * Explore alternative approaches or solutions
  * Provide more specific implementation details or recommendations
  * Consider potential challenges and mitigation strategies more thoroughly
- Final Assessment: This solution demonstrates an adequate understanding of consulting fundamentals while having room for deeper analysis and more thorough quantification.
"""
    return feedback

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

# New endpoint for solution submission and feedback generation
@router.post("/{problem_id}/submit", response_model=schemas.AIFeedback)
async def submit_solution(
    problem_id: int,
    request: Request,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """
    Submit a solution for a problem and get AI feedback
    """
    try:
        # DIAGNOSTIC: Check existing feedback scores in database
        try:
            existing_scores = db.execute(text("SELECT feedback_id, overall_score, structure_score FROM ai_feedback LIMIT 3")).fetchall()
            logger.info(f"DIAGNOSTIC - Existing scores in database: {existing_scores}")
        except Exception as e:
            logger.error(f"Diagnostic query failed: {str(e)}")
        
        # Get solution from request body (handle either format)
        request_data = await request.json()
        solution_text = request_data.get("solution", request_data.get("answer_text"))
        
        if not solution_text:
            logger.error("No solution text provided in request")
            raise HTTPException(status_code=400, detail="Solution text is required")
        
        # 1. Check if problem exists
        db_problem = db.query(models.Problem).filter(models.Problem.problem_id == problem_id).first()
        if not db_problem:
            logger.error(f"Problem with ID {problem_id} not found")
            raise HTTPException(status_code=404, detail="Problem not found")
        
        # 2. Create submission
        db_submission = models.Submission(
            user_id=current_user.user_id,
            problem_id=problem_id,
            answer_text=solution_text,  # Use the correct field name from model
            processing_status=models.ProcessingStatus.PROCESSING
        )
        db.add(db_submission)
        db.commit()
        db.refresh(db_submission)
        
        logger.info(f"Created submission {db_submission.submission_id} for problem {problem_id} by user {current_user.user_id}")

        # Load Gemini API details from environment
        GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
        # Update the URL to use the current version of the API
        # NOTE: Must use v1beta for gemini-pro, as the model is not available in v1 endpoint
        # Updated to use gemini-2.0-flash model which is the current version
        GEMINI_API_URL = os.getenv("GEMINI_API_URL", "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent")
        
        if not GEMINI_API_KEY:
            logger.error("GEMINI_API_KEY not found in environment variables")
            db_submission.processing_status = models.ProcessingStatus.FAILED
            db.commit()
            raise HTTPException(status_code=500, detail="API Key configuration error")
        
        # Prepare prompt for the AI
        prompt = ""
        problem_category = db_problem.category.lower() if db_problem.category else "problem"
        
        prompt = f"""
You are an expert consultant evaluating a response to a {problem_category}.

Here is the {problem_category}:
{db_problem.title}

{db_problem.description}

Here is the candidate's response:
{solution_text}

IMPORTANT: You must provide your evaluation in TWO PARTS:

PART 1 - SCORES (in exactly this format):
overall_score = [number between 0-10]
structure_score = [number between 0-10]
quantitative_score = [number between 0-10]
creativity_score = [number between 0-10]
communication_score = [number between 0-10]

PART 2 - FEEDBACK:
Relevance: [Yes/No] - [brief explanation]

Strengths:
* [strength 1] (only if clearly demonstrated)
* [strength 2] (only if clearly demonstrated)
* [strength 3] (only if clearly demonstrated)

Areas for Improvement:
* [area 1]
* [area 2]
* [area 3]

Final Assessment: [2-3 sentence summary without mentioning scores]

EVALUATION RULES:
- Score based on what is actually written. Do NOT assume strengths unless they are explicitly shown.
- Good answers (well-structured, thoughtful, quantitative) should be rewarded fairly with higher scores.
- Incomplete, vague, superficial, or extremely short responses must receive lower scores (5/10 or lower).
- Structure score depends on clear logical flow (steps, headings, assumptions).
- Quantitative score depends on the presence of real calculations, numbers, and reasonable assumptions.
- Creativity score reflects originality, thoughtful insights, or unique angles.
- Communication score reflects clarity, organization, and completeness.

IF the candidate only writes basic setup (e.g., assumptions without calculations), penalize structure and quantitative heavily.

Be fair, precise, and consistent in your evaluation.
"""
        
        logger.info(f"Calling Gemini API with prompt length: {len(prompt)}")
        headers = {
            "Content-Type": "application/json"
        }
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt}
                    ]
                }
            ]
        }
        
        try:
            response = requests.post(
                f"{GEMINI_API_URL}?key={GEMINI_API_KEY}",
                headers=headers,
                json=payload,
                timeout=30  # Add timeout to prevent hanging requests
            )
            
            logger.info(f"Gemini API Response Status: {response.status_code}")
            
            if response.status_code != 200:
                error_content = response.text
                logger.error(f"Gemini API Error: {error_content}")
                
                # Use mock feedback instead of failing
                logger.warning("Using mock feedback generation as fallback due to API error")
                feedback_text = generate_mock_feedback(db_problem.title, db_problem.description, solution_text)
                raw_json_response = None  # No JSON available in fallback mode
            else:
                # 4. Extract feedback from response
                api_response = response.json()
                logger.info("Gemini API response received successfully")
                
                # Check if the response has the expected structure
                try:
                    if "candidates" not in api_response or not api_response["candidates"]:
                        logger.error(f"Unexpected Gemini API response structure: {api_response}")
                        # Use fallback instead of failing
                        feedback_text = generate_mock_feedback(db_problem.title, db_problem.description, solution_text)
                        raw_json_response = None  # No JSON available in fallback mode
                    elif "content" not in api_response["candidates"][0]:
                        logger.error(f"Missing content in Gemini API response: {api_response}")
                        # Use fallback instead of failing
                        feedback_text = generate_mock_feedback(db_problem.title, db_problem.description, solution_text)
                        raw_json_response = None  # No JSON available in fallback mode
                    elif "parts" not in api_response["candidates"][0]["content"] or not api_response["candidates"][0]["content"]["parts"]:
                        logger.error(f"Missing parts in Gemini API response: {api_response}")
                        # Use fallback instead of failing
                        feedback_text = generate_mock_feedback(db_problem.title, db_problem.description, solution_text)
                        raw_json_response = None  # No JSON available in fallback mode
                    else:
                        # Extract feedback from the API response if structure is valid
                        feedback_text = api_response["candidates"][0]["content"]["parts"][0]["text"]
                        logger.info(f"Feedback generated successfully: {len(feedback_text)} characters")
                        
                        # Initialize raw_json_response to None when feedback is successfully extracted
                        raw_json_response = None
                        
                        # Initialize default scores - will be used if extraction fails
                        overall_score = 7.5  # Default fallback score
                        structure_score = 4.0
                        clarity_score = 4.0
                        creativity_score = 3.5
                        confidence_score = 4.0
                        logger.info(f"Setting initial default scores: overall={overall_score}, structure={structure_score}")
                        
                        # Log partial feedback for debugging
                        if len(feedback_text) > 200:
                            logger.info(f"End of feedback (last 200 chars): {feedback_text[-200:]}")
                        else:
                            logger.info(f"Complete feedback: {feedback_text}")
                            
                        # First check if we already have structured scores from the API response
                        structured_scores_extracted = False
                        
                        # Extract scores from structured format if available
                        if raw_json_response and isinstance(raw_json_response, dict):
                            try:
                                # Try to extract structured scores if they exist
                                if 'overall_score' in raw_json_response:
                                    overall_score = float(raw_json_response['overall_score'])
                                    structure_score = float(raw_json_response.get('structure_score', 4.0))
                                    clarity_score = float(raw_json_response.get('clarity_score', 4.0))
                                    creativity_score = float(raw_json_response.get('creativity_score', 3.5))
                                    confidence_score = float(raw_json_response.get('confidence_score', 4.0))
                                    structured_scores_extracted = True
                                    logger.info(f"Successfully extracted scores from structured API response")
                            except Exception as ex:
                                logger.error(f"Failed to extract structured scores: {str(ex)}")
                        
                        # Extract scores from text with regex if we don't have structured scores
                        try:
                            if not structured_scores_extracted:
                                logger.info("Attempting to extract scores from text feedback")
                                
                                # Try to extract scores using the "score = X" format first (from prompt)
                                score_format_1_extracted = False
                                
                                # Extract scores using regex patterns for "overall_score = X" format
                                overall_match = re.search(r'overall_score\s*=\s*(\d+(?:\.\d+)?)', feedback_text, re.IGNORECASE)
                                if overall_match:
                                    overall_score = float(overall_match.group(1))
                                    score_format_1_extracted = True
                                    logger.info(f"Extracted overall score (format 1): {overall_score}")
                                    
                                structure_match = re.search(r'structure_score\s*=\s*(\d+(?:\.\d+)?)', feedback_text, re.IGNORECASE)
                                if structure_match:
                                    structure_score = float(structure_match.group(1))
                                    score_format_1_extracted = True
                                    logger.info(f"Extracted structure score (format 1): {structure_score}")
                                    
                                quantitative_match = re.search(r'quantitative_score\s*=\s*(\d+(?:\.\d+)?)', feedback_text, re.IGNORECASE)
                                if quantitative_match:
                                    quantitative_score = float(quantitative_match.group(1))
                                    clarity_score = quantitative_score  # Map quantitative score to clarity
                                    score_format_1_extracted = True
                                    logger.info(f"Extracted quantitative/clarity score (format 1): {clarity_score}")
                                    
                                creativity_match = re.search(r'creativity_score\s*=\s*(\d+(?:\.\d+)?)', feedback_text, re.IGNORECASE)
                                if creativity_match:
                                    creativity_score = float(creativity_match.group(1))
                                    score_format_1_extracted = True
                                    logger.info(f"Extracted creativity score (format 1): {creativity_score}")
                                    
                                communication_match = re.search(r'communication_score\s*=\s*(\d+(?:\.\d+)?)', feedback_text, re.IGNORECASE)
                                if communication_match:
                                    communication_score = float(communication_match.group(1))
                                    confidence_score = communication_score  # Map communication score to confidence
                                    score_format_1_extracted = True
                                    logger.info(f"Extracted communication/confidence score (format 1): {confidence_score}")
                                
                                if score_format_1_extracted:
                                    logger.info("Successfully extracted at least some scores using 'score = X' format")
                                
                                # Extract scores using common patterns found in actual API responses
                                # These patterns cover both "Score: X/10" and "Score: X" formats with optional space after colon
                                
                                # Overall score - multiple possible formats
                                overall_patterns = [
                                    r'Overall Score:?\s*(\d+(?:\.\d+)?)\s*(?:\/\s*10)?',
                                    r'Overall:?\s*(\d+(?:\.\d+)?)\s*(?:\/\s*10)?',
                                    r'Overall Rating:?\s*(\d+(?:\.\d+)?)\s*(?:\/\s*10)?',
                                    r'Final Score:?\s*(\d+(?:\.\d+)?)\s*(?:\/\s*10)?'
                                ]
                                
                                for pattern in overall_patterns:
                                    overall_match = re.search(pattern, feedback_text, re.IGNORECASE)
                                    if overall_match:
                                        overall_score = float(overall_match.group(1))
                                        logger.info(f"Extracted overall score (format 2): {overall_score} using pattern: {pattern}")
                                        break
                                
                                # Structure score - handles various structure label formats
                                structure_patterns = [
                                    r'Structure[^:]*:?\s*(\d+(?:\.\d+)?)\s*(?:\/\s*10)?',
                                    r'Structure & Framework:?\s*(\d+(?:\.\d+)?)\s*(?:\/\s*10)?',
                                    r'Framework:?\s*(\d+(?:\.\d+)?)\s*(?:\/\s*10)?',
                                    r'Structure Score:?\s*(\d+(?:\.\d+)?)\s*(?:\/\s*10)?'
                                ]
                                
                                for pattern in structure_patterns:
                                    structure_match = re.search(pattern, feedback_text, re.IGNORECASE)
                                    if structure_match:
                                        structure_score = float(structure_match.group(1))
                                        logger.info(f"Extracted structure score: {structure_score} using pattern: {pattern}")
                                        break
                                
                                # Clarity/Quantitative score - various possible labels
                                clarity_patterns = [
                                    r'Quantitative Analysis:?\s*(\d+(?:\.\d+)?)\s*(?:\/\s*10)?',
                                    r'Quantitative:?\s*(\d+(?:\.\d+)?)\s*(?:\/\s*10)?',
                                    r'Assumptions Quality:?\s*(\d+(?:\.\d+)?)\s*(?:\/\s*10)?',
                                    r'Assumptions:?\s*(\d+(?:\.\d+)?)\s*(?:\/\s*10)?',
                                    r'Clarity:?\s*(\d+(?:\.\d+)?)\s*(?:\/\s*10)?',
                                    r'Analysis:?\s*(\d+(?:\.\d+)?)\s*(?:\/\s*10)?'
                                ]
                                
                                for pattern in clarity_patterns:
                                    clarity_match = re.search(pattern, feedback_text, re.IGNORECASE)
                                    if clarity_match:
                                        clarity_score = float(clarity_match.group(1))
                                        logger.info(f"Extracted clarity/quantitative score: {clarity_score} using pattern: {pattern}")
                                        break
                                
                                # Creativity score
                                creativity_patterns = [
                                    r'Creativity:?\s*(\d+(?:\.\d+)?)\s*(?:\/\s*10)?',
                                    r'Creativity Score:?\s*(\d+(?:\.\d+)?)\s*(?:\/\s*10)?',
                                    r'Analysis Quality:?\s*(\d+(?:\.\d+)?)\s*(?:\/\s*10)?',
                                    r'Math Accuracy:?\s*(\d+(?:\.\d+)?)\s*(?:\/\s*10)?',
                                    r'Innovation:?\s*(\d+(?:\.\d+)?)\s*(?:\/\s*10)?'
                                ]
                                
                                for pattern in creativity_patterns:
                                    creativity_match = re.search(pattern, feedback_text, re.IGNORECASE)
                                    if creativity_match:
                                        creativity_score = float(creativity_match.group(1))
                                        logger.info(f"Extracted creativity score: {creativity_score} using pattern: {pattern}")
                                        break
                                
                                # Communication score
                                communication_patterns = [
                                    r'Communication:?\s*(\d+(?:\.\d+)?)\s*(?:\/\s*10)?',
                                    r'Communication Score:?\s*(\d+(?:\.\d+)?)\s*(?:\/\s*10)?',
                                    r'Communication Clarity:?\s*(\d+(?:\.\d+)?)\s*(?:\/\s*10)?',
                                    r'Clarity of Communication:?\s*(\d+(?:\.\d+)?)\s*(?:\/\s*10)?',
                                    r'Presentation:?\s*(\d+(?:\.\d+)?)\s*(?:\/\s*10)?'
                                ]
                                
                                for pattern in communication_patterns:
                                    communication_match = re.search(pattern, feedback_text, re.IGNORECASE)
                                    if communication_match:
                                        confidence_score = float(communication_match.group(1))
                                        logger.info(f"Extracted communication/confidence score: {confidence_score} using pattern: {pattern}")
                                        break
                                
                                # Make sure scores are within valid range
                                overall_score = max(0, min(10, overall_score))
                                structure_score = max(0, min(10, structure_score))
                                clarity_score = max(0, min(10, clarity_score))
                                creativity_score = max(0, min(10, creativity_score))
                                confidence_score = max(0, min(10, confidence_score))
                                
                                logger.info(f"Final extracted scores: overall={overall_score}, structure={structure_score}, "
                                          f"clarity={clarity_score}, creativity={creativity_score}, confidence={confidence_score}")
                        except Exception as score_error:
                            logger.exception(f"Error extracting scores from feedback: {str(score_error)}")
                            logger.warning("Using default fallback scores due to extraction failure")
                            # Keep using default scores set above

                except Exception as e:
                    logger.exception(f"Error processing API response: {str(e)}")
                    # Use mock feedback instead of failing
                    feedback_text = generate_mock_feedback(db_problem.title, db_problem.description, solution_text)
                    raw_json_response = None  # No JSON available in fallback mode
            
        except requests.RequestException as req_err:
            logger.exception(f"Request to Gemini API failed: {str(req_err)}")
            # Use mock feedback instead of failing
            feedback_text = generate_mock_feedback(db_problem.title, db_problem.description, solution_text)
            raw_json_response = None  # No JSON available in fallback mode
        except ValueError as ve:
            logger.exception(f"Error parsing Gemini API response: {str(ve)}")
            # Use mock feedback instead of failing
            feedback_text = generate_mock_feedback(db_problem.title, db_problem.description, solution_text)
            raw_json_response = None  # No JSON available in fallback mode
        except Exception as e:
            logger.exception(f"Unexpected error during Gemini API interaction: {str(e)}")
            # Use mock feedback instead of failing
            feedback_text = generate_mock_feedback(db_problem.title, db_problem.description, solution_text)
            raw_json_response = None  # No JSON available in fallback mode
        
        # 5. Store feedback in database (this code will execute regardless of API success or failure)
        # We've already extracted scores, so there's no need to re-check or re-extract
        try:
            # Check if scores are already present in the feedback
            has_score_header = re.search(r'(Structure|Assumptions|Math Accuracy|Overall Score):?\s*\d+(?:\.\d+)?\/10', feedback_text)
            
            if not has_score_header:
                # Remove any existing score-like patterns to avoid duplication
                clean_feedback = re.sub(r'(Structure|Approach|Assumptions|Math Accuracy):.*?(\d+(?:\.\d+)?)/10', '', feedback_text, flags=re.IGNORECASE)
                clean_feedback = re.sub(r'Overall Score:.*?(\d+(?:\.\d+)?)/10', '', clean_feedback, flags=re.IGNORECASE)
                clean_feedback = re.sub(r'overall_score\s*=\s*\d+(?:\.\d+)?', '', clean_feedback, flags=re.IGNORECASE)
                clean_feedback = re.sub(r'structure_score\s*=\s*\d+(?:\.\d+)?', '', clean_feedback, flags=re.IGNORECASE)
                clean_feedback = re.sub(r'quantitative_score\s*=\s*\d+(?:\.\d+)?', '', clean_feedback, flags=re.IGNORECASE)
                clean_feedback = re.sub(r'creativity_score\s*=\s*\d+(?:\.\d+)?', '', clean_feedback, flags=re.IGNORECASE)
                clean_feedback = re.sub(r'communication_score\s*=\s*\d+(?:\.\d+)?', '', clean_feedback, flags=re.IGNORECASE)
                
                # Construct a new header with the scores
                score_header = ""
                if db_problem.category == "Case Study":
                    score_header = f"""
Score Summary:
Overall Score: {overall_score}/10
Structure & Framework: {structure_score}/10
Assumptions Quality: {clarity_score}/10
Analysis Quality: {creativity_score}/10
Communication: {confidence_score}/10

"""
                elif db_problem.category == "Guesstimate":
                    score_header = f"""
Score Summary:
Overall Score: {overall_score}/10
Structure: {structure_score}/10
Assumptions: {clarity_score}/10
Math Accuracy: {creativity_score}/10
Communication: {confidence_score}/10

"""
                else:
                    score_header = f"""
Score Summary:
Overall Score: {overall_score}/10
Structure: {structure_score}/10
Quantitative Analysis: {clarity_score}/10
Creativity: {creativity_score}/10
Communication: {confidence_score}/10

"""
                # Combine header with existing feedback
                feedback_text = score_header.strip() + "\n\n" + clean_feedback.strip()
                logger.info("Added formatted score header to feedback text")
                
            logger.info(f"Final scores - Overall: {overall_score}, Structure: {structure_score}, "
                      f"Clarity: {clarity_score}, Creativity: {creativity_score}, Confidence: {confidence_score}")
                
        except Exception as format_error:
            logger.exception(f"Error formatting feedback with scores: {str(format_error)}")
            # Continue with original feedback text

        # Create the AIFeedback object and save it to database with explicit values
        try:
            # Use SQLAlchemy ORM instead of raw SQL to avoid schema mismatch issues
            ai_feedback = models.AIFeedback(
                submission_id=db_submission.submission_id,
                overall_score=float(overall_score),
                feedback_text=feedback_text,
                structure_score=float(structure_score),
                clarity_score=float(clarity_score if 'quantitative_score' not in locals() else quantitative_score),
                creativity_score=float(creativity_score),
                confidence_score=float(confidence_score if 'communication_score' not in locals() else communication_score),
                model_version="gemini-2.0-flash",
                generated_at=datetime.now()
            )
            
            db.add(ai_feedback)
            db.commit()
            db.refresh(ai_feedback)
            
            # Print scores to terminal
            print(f"\nScores for submission {db_submission.submission_id}:")
            print(f"Overall Score: {overall_score}")
            print(f"Structure Score: {structure_score}") 
            print(f"Clarity Score: {clarity_score}")
            print(f"Creativity Score: {creativity_score}")
            print(f"Confidence Score: {confidence_score}\n")
            
            # Update the submission status
            db_submission.processing_status = models.ProcessingStatus.COMPLETED
            db.commit()
            
            # Log success
            logger.info(f"Successfully inserted AIFeedback with ID {ai_feedback.feedback_id} using ORM")
            logger.info(f"Scores: Overall={overall_score}, Structure={structure_score}, Clarity={clarity_score}, Creativity={creativity_score}")
            
        except Exception as e:
            logger.error(f"Error saving feedback to database: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            
            # Try again with a more direct approach
            try:
                # Create a new session to avoid any lingering transaction issues
                new_db = database.SessionLocal()
                
                # Create the feedback object again
                ai_feedback = models.AIFeedback(
                    submission_id=db_submission.submission_id,
                    feedback_text=feedback_text,
                    overall_score=float(overall_score),
                    structure_score=float(structure_score),
                    clarity_score=float(clarity_score if 'quantitative_score' not in locals() else quantitative_score),
                    creativity_score=float(creativity_score),
                    confidence_score=float(confidence_score if 'communication_score' not in locals() else communication_score),
                    model_version="gemini-2.0-flash",
                    generated_at=datetime.now()
                )
                
                # Add to new session and commit
                new_db.add(ai_feedback)
                new_db.commit()
                new_db.refresh(ai_feedback)
                
                # Update submission status
                db_submission.processing_status = models.ProcessingStatus.COMPLETED
                new_db.add(db_submission)
                new_db.commit()
                
                # Close the new session
                new_db.close()
                
                logger.info("Successfully saved feedback using alternative session")
            except Exception as inner_e:
                logger.error(f"Second attempt also failed: {str(inner_e)}")
                # If all else fails, return a mock object to avoid crashing the UI
                ai_feedback = models.AIFeedback(
                    feedback_id=-1,  # Dummy ID
                    submission_id=db_submission.submission_id,
                    feedback_text="We encountered an error saving your feedback. Please try again.",
                    overall_score=7.0,
                    structure_score=7.0,
                    clarity_score=7.0,
                    creativity_score=7.0,
                    confidence_score=7.0,
                    model_version="error-recovery",
                    generated_at=datetime.now()
                )
                logger.warning("Returning mock feedback object due to database errors")
        
        return ai_feedback
            
    except HTTPException:
        # Re-raise HTTP exceptions to preserve their status codes and details
        raise
    except Exception as e:
        logger.exception(f"Error in submit_solution: {str(e)}")
        # Handle errors and update submission if it exists
        try:
            if 'db_submission' in locals():
                db_submission.processing_status = models.ProcessingStatus.FAILED
                db.commit()
        except:
            pass  # If we can't update the submission, just continue to the exception
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

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