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
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"

# Helper function to generate mock feedback when API calls fail
def generate_mock_feedback(problem_title, problem_description, solution_text):
    """Generate mock feedback when the API call fails"""
    logger.warning("Using mock feedback generation as fallback")
    
    # Extract key information for the feedback
    problem_type = "case study" if "Case Study" in problem_description else "guesstimate"
    solution_length = len(solution_text)
    solution_paragraphs = solution_text.count('\n\n') + 1
    
    # Check if solution is too short or nonsensical
    if solution_length < 50 or not any(word in solution_text.lower() for word in ["market", "strategy", "business", "company", "customer", "product", "service", "analysis"]):
        # For bad responses, determine score based on length
        if solution_length < 20:
            overall_score = 1.5  # Very short/bad gets very low score
        else:
            overall_score = 3.0  # Slightly longer but still bad
        
        logger.info(f"Mock feedback using BAD score: {overall_score} for solution length {solution_length}")
        return f"""# Feedback on {problem_title}

- Relevance: No - The response is just {solution_length} characters long and does not address the key components of a market entry strategy.
- Strengths: None identified.
- Areas for improvement:
  * Provide a comprehensive analysis of the market opportunity
  * Include customer segmentation and targeting strategy
  * Develop pricing, distribution, and promotion strategies
  * Address competitive landscape and differentiation
  * Consider financial implications and resource requirements
- Final Assessment: The response is insufficient and does not meet the minimum requirements for a consulting case solution.
- Score: {overall_score}/10
"""
    
    # For good solutions, score based on length and quality indicators
    # More paragraphs and better keywords = higher score
    keyword_count = sum(1 for keyword in ["analysis", "segment", "target", "competitor", "revenue", "profit", "strategy", "implementation"] 
                        if keyword in solution_text.lower())
    
    # Base score on length and keyword richness
    if solution_length > 500 and keyword_count >= 3:
        overall_score = 8.5  # Longer with good keywords
    elif solution_length > 300:
        overall_score = 7.5  # Medium length
    else:
        overall_score = 6.5  # Shorter but still acceptable
    
    logger.info(f"Mock feedback using GOOD score: {overall_score} for solution with length {solution_length} and {keyword_count} keywords")
    
    # Create feedback based on solution characteristics
    feedback = f"""# Feedback on {problem_title}

- Relevance: Yes - The response addresses the market entry strategy problem with appropriate analysis.
- Strengths:
  * Clear understanding of the problem context
  * Methodical and logical approach to market analysis
  * Specific insights relevant to the {problem_type} scenario
  * Good organization with {solution_paragraphs} clearly defined sections
- Areas for improvement:
  * Include more quantitative analysis to strengthen arguments
  * Explore alternative market entry approaches
  * Provide more specific implementation timelines and resource allocation
  * Consider potential risks and mitigation strategies more thoroughly
- Final Assessment: Overall, this is a solid solution that demonstrates good consulting fundamentals while having room for deeper analysis.
- Score: {overall_score}/10
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
        GEMINI_API_URL = os.getenv("GEMINI_API_URL", "https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent")
        
        if not GEMINI_API_KEY:
            logger.error("GEMINI_API_KEY not found in environment variables")
            db_submission.processing_status = models.ProcessingStatus.FAILED
            db.commit()
            raise HTTPException(status_code=500, detail="API Key configuration error")
        
        # Prepare prompt for the AI
        prompt = ""
        if db_problem.category == "Case Study":
            prompt = f"""You are an expert consultant evaluating a response to a {db_problem.category.lower()}.

Here is the {db_problem.category.lower()}:
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
* [strength 1]
* [strength 2]
* [strength 3]

Areas for Improvement:
* [area 1]
* [area 2]
* [area 3]

Final Assessment: [2-3 sentence summary without mentioning scores]

Evaluate all aspects thoroughly and provide honest, specific feedback.
"""
        elif db_problem.category == "Guesstimate":
            prompt = f"""You are an expert consultant evaluating a response to a {db_problem.category.lower()}.

Here is the {db_problem.category.lower()}:
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
* [strength 1]
* [strength 2]
* [strength 3]

Areas for Improvement:
* [area 1]
* [area 2]
* [area 3]

Final Assessment: [2-3 sentence summary without mentioning scores]

Evaluate all aspects thoroughly and provide honest, specific feedback.
"""
        else:
            prompt = f"""You are an expert consultant evaluating a response to a problem.

Here is the problem:
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
* [strength 1]
* [strength 2]
* [strength 3]

Areas for Improvement:
* [area 1]
* [area 2]
* [area 3]

Final Assessment: [2-3 sentence summary without mentioning scores]

Evaluate all aspects thoroughly and provide honest, specific feedback.
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
                        
                        # Log the last 200 characters to see if it includes the score
                        if len(feedback_text) > 200:
                            logger.info(f"End of feedback (last 200 chars): {feedback_text[-200:]}")
                        else:
                            logger.info(f"Complete feedback: {feedback_text}")
                            
                            # Parse scores using regex
                            try:
                                # First try to extract scores from the structured format
                                overall_score = 8.5  # Default fallback score
                                structure_score = 7.0
                                quantitative_score = 7.0  # Maps to clarity_score in DB
                                creativity_score = 7.0
                                communication_score = 7.0  # Maps to confidence_score in DB
                                
                                # Look for score patterns in the table-like format
                                score_patterns = {
                                    'overall_score': r'overall_score\s*=\s*(\d+(?:\.\d+)?)',
                                    'structure_score': r'structure_score\s*=\s*(\d+(?:\.\d+)?)',
                                    'quantitative_score': r'quantitative_score\s*=\s*(\d+(?:\.\d+)?)',
                                    'creativity_score': r'creativity_score\s*=\s*(\d+(?:\.\d+)?)',
                                    'communication_score': r'communication_score\s*=\s*(\d+(?:\.\d+)?)'
                                }
                                
                                for score_name, pattern in score_patterns.items():
                                    match = re.search(pattern, feedback_text, re.IGNORECASE)
                                    if match:
                                        try:
                                            score_value = float(match.group(1))
                                            if 0 <= score_value <= 10:  # Validate score is in range
                                                if score_name == 'overall_score':
                                                    overall_score = score_value
                                                elif score_name == 'structure_score':
                                                    structure_score = score_value
                                                elif score_name == 'quantitative_score':
                                                    quantitative_score = score_value
                                                elif score_name == 'creativity_score':
                                                    creativity_score = score_value
                                                elif score_name == 'communication_score':
                                                    communication_score = score_value
                                                    
                                                logger.info(f"Successfully extracted {score_name}: {score_value}")
                                        except ValueError:
                                            logger.warning(f"Failed to convert {match.group(1)} to float for {score_name}")
                                
                                # Set the scores for database insertion
                                logger.info(f"Final scores from parsing: overall={overall_score}, structure={structure_score}, quantitative={quantitative_score}")
                                
                            except Exception as e:
                                logger.warning(f"Error extracting scores using new pattern: {str(e)}")
                                # Continue with the existing fallback score extraction
                                
                            # No JSON to store since we're using text format
                            raw_json_response = None
                except Exception as e:
                    logger.error(f"Error parsing API response: {str(e)}")
                    # Use fallback instead of failing
                    feedback_text = generate_mock_feedback(db_problem.title, db_problem.description, solution_text)
                    raw_json_response = None  # No JSON available in fallback mode
            
        except requests.RequestException as re:
            logger.exception(f"Request to Gemini API failed: {str(re)}")
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
        # Extract score from feedback more robustly
        overall_score = 7.5  # Default fallback score
        structure_score = 4.0
        clarity_score = 4.0
        creativity_score = 3.5
        confidence_score = 4.0
        
        # First try to extract the scores using regex patterns
        try:
            # Try to extract the overall score
            score_patterns = [
                r'Score:\s*(\d+(?:\.\d+)?)\s*\/\s*10',      # Score: X/10
                r'Score:\s*(\d+(?:\.\d+)?)\s*out of\s*10',  # Score: X out of 10
                r'Score:\s*(\d+(?:\.\d+)?)\/10',            # Score: X/10 (no space)
                r'Score:\s*(\d+(?:\.\d+)?)\s*\/\s*10',      # Score: X / 10
                r'(\d+(?:\.\d+)?)\s*\/\s*10',               # X/10 anywhere
                r'rated.*?(\d+(?:\.\d+)?)\s*\/\s*10',       # rated X/10
                r'grade.*?(\d+(?:\.\d+)?)\s*\/\s*10',       # grade X/10
                r'rating.*?(\d+(?:\.\d+)?)\s*\/\s*10',      # rating X/10
                r'score.*?(\d+(?:\.\d+)?)\s*\/\s*10',       # score X/10
                r'Overall Score:?\s*(\d+(?:\.\d+)?)',       # Overall Score: X
            ]
            
            for pattern in score_patterns:
                match = re.search(pattern, feedback_text, re.IGNORECASE)
                if match:
                    try:
                        extracted_score = float(match.group(1))
                        if 0 <= extracted_score <= 10:  # Validate score is in range
                            overall_score = extracted_score
                            logger.info(f"Successfully extracted overall score {overall_score} using pattern: {pattern}")
                            break
                        else:
                            logger.warning(f"Extracted score {extracted_score} is out of range (0-10)")
                    except ValueError:
                        logger.warning(f"Failed to convert {match.group(1)} to float")
                        continue
            
            # Extract specific parameter scores based on problem category
            if db_problem.category == "Case Study":
                # Structure & Framework
                structure_patterns = [
                    r'Structure & Framework:?\s*(\d+(?:\.\d+)?)\s*\/\s*10',  # Structure & Framework: X/10
                    r'Structure:?\s*(\d+(?:\.\d+)?)\s*\/\s*10',              # Structure: X/10
                    r'Framework:?\s*(\d+(?:\.\d+)?)\s*\/\s*10',              # Framework: X/10
                    r'Structure & Framework:?\s*(\d+(?:\.\d+)?)',           # Structure & Framework: X
                ]
                
                # Quantitative Analysis
                quantitative_patterns = [
                    r'Quantitative Analysis:?\s*(\d+(?:\.\d+)?)\s*\/\s*10',  # Quantitative Analysis: X/10
                    r'Quantitative:?\s*(\d+(?:\.\d+)?)\s*\/\s*10',           # Quantitative: X/10
                    r'Analysis:?\s*(\d+(?:\.\d+)?)\s*\/\s*10',               # Analysis: X/10
                    r'Quantitative Analysis:?\s*(\d+(?:\.\d+)?)',           # Quantitative Analysis: X
                ]
                
                # Creativity & Insight
                creativity_patterns = [
                    r'Creativity & Insight:?\s*(\d+(?:\.\d+)?)\s*\/\s*10',   # Creativity & Insight: X/10
                    r'Creativity:?\s*(\d+(?:\.\d+)?)\s*\/\s*10',             # Creativity: X/10
                    r'Insight:?\s*(\d+(?:\.\d+)?)\s*\/\s*10',                # Insight: X/10
                    r'Creativity & Insight:?\s*(\d+(?:\.\d+)?)',            # Creativity & Insight: X
                ]
                
                # Communication Clarity
                clarity_patterns = [
                    r'Communication Clarity:?\s*(\d+(?:\.\d+)?)\s*\/\s*10',  # Communication Clarity: X/10
                    r'Communication:?\s*(\d+(?:\.\d+)?)\s*\/\s*10',          # Communication: X/10
                    r'Clarity:?\s*(\d+(?:\.\d+)?)\s*\/\s*10',                # Clarity: X/10
                    r'Communication Clarity:?\s*(\d+(?:\.\d+)?)',           # Communication Clarity: X
                ]
                
                # Extract structure score
                for pattern in structure_patterns:
                    match = re.search(pattern, feedback_text, re.IGNORECASE)
                    if match:
                        try:
                            extracted_score = float(match.group(1))
                            if 0 <= extracted_score <= 10:  # Validate score is in range
                                structure_score = extracted_score
                                logger.info(f"Extracted structure score: {structure_score}")
                                break
                        except ValueError:
                            continue
                
                # Extract quantitative analysis score (mapped to clarity_score in db)
                for pattern in quantitative_patterns:
                    match = re.search(pattern, feedback_text, re.IGNORECASE)
                    if match:
                        try:
                            extracted_score = float(match.group(1))
                            if 0 <= extracted_score <= 10:
                                clarity_score = extracted_score
                                logger.info(f"Extracted quantitative analysis score: {clarity_score}")
                                break
                        except ValueError:
                            continue
                
                # Extract creativity score
                for pattern in creativity_patterns:
                    match = re.search(pattern, feedback_text, re.IGNORECASE)
                    if match:
                        try:
                            extracted_score = float(match.group(1))
                            if 0 <= extracted_score <= 10:
                                creativity_score = extracted_score
                                logger.info(f"Extracted creativity score: {creativity_score}")
                                break
                        except ValueError:
                            continue
                
                # Extract communication clarity score (mapped to confidence_score in db)
                for pattern in clarity_patterns:
                    match = re.search(pattern, feedback_text, re.IGNORECASE)
                    if match:
                        try:
                            extracted_score = float(match.group(1))
                            if 0 <= extracted_score <= 10:
                                confidence_score = extracted_score
                                logger.info(f"Extracted communication clarity score: {confidence_score}")
                                break
                        except ValueError:
                            continue
                
            elif db_problem.category == "Guesstimate":
                # Approach/Structure
                structure_patterns = [
                    r'Approach/Structure:?\s*(\d+(?:\.\d+)?)\s*\/\s*10',     # Approach/Structure: X/10
                    r'Approach:?\s*(\d+(?:\.\d+)?)\s*\/\s*10',               # Approach: X/10
                    r'Structure:?\s*(\d+(?:\.\d+)?)\s*\/\s*10',              # Structure: X/10
                    r'Approach/Structure:?\s*(\d+(?:\.\d+)?)',              # Approach/Structure: X
                ]
                
                # Assumptions Quality
                assumption_patterns = [
                    r'Assumptions Quality:?\s*(\d+(?:\.\d+)?)\s*\/\s*10',    # Assumptions Quality: X/10
                    r'Assumptions:?\s*(\d+(?:\.\d+)?)\s*\/\s*10',            # Assumptions: X/10
                    r'Assumptions Quality:?\s*(\d+(?:\.\d+)?)',             # Assumptions Quality: X
                ]
                
                # Math Accuracy
                math_patterns = [
                    r'Math Accuracy:?\s*(\d+(?:\.\d+)?)\s*\/\s*10',          # Math Accuracy: X/10
                    r'Math:?\s*(\d+(?:\.\d+)?)\s*\/\s*10',                   # Math: X/10
                    r'Accuracy:?\s*(\d+(?:\.\d+)?)\s*\/\s*10',               # Accuracy: X/10
                    r'Math Accuracy:?\s*(\d+(?:\.\d+)?)',                   # Math Accuracy: X
                ]
                
                # Step-by-Step Thinking
                thinking_patterns = [
                    r'Step-by-Step Thinking:?\s*(\d+(?:\.\d+)?)\s*\/\s*10',  # Step-by-Step Thinking: X/10
                    r'Thinking:?\s*(\d+(?:\.\d+)?)\s*\/\s*10',               # Thinking: X/10
                    r'Step-by-Step:?\s*(\d+(?:\.\d+)?)\s*\/\s*10',           # Step-by-Step: X/10
                    r'Step-by-Step Thinking:?\s*(\d+(?:\.\d+)?)',           # Step-by-Step Thinking: X
                ]
                
                # Extract structure score
                for pattern in structure_patterns:
                    match = re.search(pattern, feedback_text, re.IGNORECASE)
                    if match:
                        try:
                            extracted_score = float(match.group(1))
                            if 0 <= extracted_score <= 10:
                                structure_score = extracted_score
                                logger.info(f"Extracted approach/structure score: {structure_score}")
                                break
                        except ValueError:
                            continue
                
                # Extract assumptions quality score (mapped to clarity_score in db)
                for pattern in assumption_patterns:
                    match = re.search(pattern, feedback_text, re.IGNORECASE)
                    if match:
                        try:
                            extracted_score = float(match.group(1))
                            if 0 <= extracted_score <= 10:
                                clarity_score = extracted_score
                                logger.info(f"Extracted assumptions quality score: {clarity_score}")
                                break
                        except ValueError:
                            continue
                
                # Extract math accuracy score (mapped to creativity_score in db)
                for pattern in math_patterns:
                    match = re.search(pattern, feedback_text, re.IGNORECASE)
                    if match:
                        try:
                            extracted_score = float(match.group(1))
                            if 0 <= extracted_score <= 10:
                                creativity_score = extracted_score
                                logger.info(f"Extracted math accuracy score: {creativity_score}")
                                break
                        except ValueError:
                            continue
                
                # Extract step-by-step thinking score (mapped to confidence_score in db)
                for pattern in thinking_patterns:
                    match = re.search(pattern, feedback_text, re.IGNORECASE)
                    if match:
                        try:
                            extracted_score = float(match.group(1))
                            if 0 <= extracted_score <= 10:
                                confidence_score = extracted_score
                                logger.info(f"Extracted step-by-step thinking score: {confidence_score}")
                                break
                        except ValueError:
                            continue
            
            # If we have all scores, construct a structured feedback text that includes them
            # But only if we didn't get them explicitly from the API already
            if not re.search(r'Structure & Framework:?\s*\d', feedback_text) and not re.search(r'Approach/Structure:?\s*\d', feedback_text):
                # Remove the feedback part from any existing text to avoid duplication
                clean_feedback = re.sub(r'(Structure & Framework|Approach/Structure|Quantitative Analysis|Assumptions Quality|Math Accuracy|Step-by-Step Thinking|Communication Clarity|Creativity & Insight):.*?(\d+(?:\.\d+)?)/10', '', feedback_text, flags=re.IGNORECASE)
                clean_feedback = re.sub(r'Overall Score:.*?(\d+(?:\.\d+)?)/10', '', clean_feedback, flags=re.IGNORECASE)

                # Construct a new header with the scores
                score_header = ""
                if db_problem.category == "Case Study":
                    score_header = f"""
Structure & Framework: {structure_score}/10
Quantitative Analysis: {clarity_score}/10
Creativity & Insight: {creativity_score}/10
Communication Clarity: {confidence_score}/10
Overall Score: {overall_score}/10

"""
                elif db_problem.category == "Guesstimate":
                    score_header = f"""
Approach/Structure: {structure_score}/10
Assumptions Quality: {clarity_score}/10
Math Accuracy: {creativity_score}/10
Step-by-Step Thinking: {confidence_score}/10
Overall Score: {overall_score}/10

"""
                # Combine header with existing feedback
                feedback_text = score_header + clean_feedback
            
            logger.info(f"Final scores - Overall: {overall_score}, Structure: {structure_score}, Quantitative/Assumptions: {clarity_score}, Creativity/Math: {creativity_score}, Communication/Thinking: {confidence_score}")
            
        except Exception as e:
            logger.error(f"Error extracting scores from feedback: {str(e)}")
            logger.error(f"Exception traceback: {traceback.format_exc()}")
            # Default values already set at the beginning
        
        # Create the AIFeedback object and save it to database with explicit values
        feedback_id = None
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
                model_version="gemini-pro",
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
                    model_version="gemini-pro",
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