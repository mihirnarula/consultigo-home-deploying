from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .. import models, schemas, database
from typing import List

router = APIRouter(
    prefix="/problems",
    tags=["problems"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=schemas.Problem, status_code=status.HTTP_201_CREATED)
def create_problem(problem: schemas.ProblemCreate, author_id: int, db: Session = Depends(database.get_db)):
    # Check if user exists
    user = db.query(models.User).filter(models.User.user_id == author_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Create problem
    db_problem = models.Problem(
        title=problem.title,
        description=problem.description,
        difficulty=problem.difficulty,
        category=problem.category,
        estimated_time=problem.estimated_time,
        is_active=problem.is_active,
        author_id=author_id
    )
    db.add(db_problem)
    db.commit()
    db.refresh(db_problem)
    return db_problem

@router.get("/", response_model=List[schemas.Problem])
def read_problems(skip: int = 0, limit: int = 100, category: str = None, difficulty: schemas.DifficultyLevel = None, 
                 db: Session = Depends(database.get_db)):
    query = db.query(models.Problem)
    
    if category:
        query = query.filter(models.Problem.category == category)
    
    if difficulty:
        query = query.filter(models.Problem.difficulty == difficulty)
    
    problems = query.offset(skip).limit(limit).all()
    return problems

@router.get("/{problem_id}", response_model=schemas.Problem)
def read_problem(problem_id: int, db: Session = Depends(database.get_db)):
    db_problem = db.query(models.Problem).filter(models.Problem.problem_id == problem_id).first()
    if db_problem is None:
        raise HTTPException(status_code=404, detail="Problem not found")
    return db_problem

@router.put("/{problem_id}", response_model=schemas.Problem)
def update_problem(problem_id: int, problem: schemas.ProblemUpdate, db: Session = Depends(database.get_db)):
    db_problem = db.query(models.Problem).filter(models.Problem.problem_id == problem_id).first()
    if db_problem is None:
        raise HTTPException(status_code=404, detail="Problem not found")
    
    update_data = problem.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_problem, key, value)
    
    db.commit()
    db.refresh(db_problem)
    return db_problem

@router.delete("/{problem_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_problem(problem_id: int, db: Session = Depends(database.get_db)):
    db_problem = db.query(models.Problem).filter(models.Problem.problem_id == problem_id).first()
    if db_problem is None:
        raise HTTPException(status_code=404, detail="Problem not found")
    
    db.delete(db_problem)
    db.commit()
    return None

# Problem Examples endpoints
@router.post("/{problem_id}/examples", response_model=schemas.ProblemExample, status_code=status.HTTP_201_CREATED)
def create_problem_example(problem_id: int, example: schemas.ProblemExampleBase, db: Session = Depends(database.get_db)):
    # Check if problem exists
    db_problem = db.query(models.Problem).filter(models.Problem.problem_id == problem_id).first()
    if db_problem is None:
        raise HTTPException(status_code=404, detail="Problem not found")
    
    # Create example
    db_example = models.ProblemExample(
        problem_id=problem_id,
        example_text=example.example_text,
        example_answer=example.example_answer
    )
    db.add(db_example)
    db.commit()
    db.refresh(db_example)
    return db_example

@router.get("/{problem_id}/examples", response_model=List[schemas.ProblemExample])
def read_problem_examples(problem_id: int, db: Session = Depends(database.get_db)):
    # Check if problem exists
    db_problem = db.query(models.Problem).filter(models.Problem.problem_id == problem_id).first()
    if db_problem is None:
        raise HTTPException(status_code=404, detail="Problem not found")
    
    examples = db.query(models.ProblemExample).filter(models.ProblemExample.problem_id == problem_id).all()
    return examples

# Framework endpoints
@router.post("/{problem_id}/frameworks", response_model=schemas.Framework, status_code=status.HTTP_201_CREATED)
def create_framework(problem_id: int, framework: schemas.FrameworkBase, db: Session = Depends(database.get_db)):
    # Check if problem exists
    db_problem = db.query(models.Problem).filter(models.Problem.problem_id == problem_id).first()
    if db_problem is None:
        raise HTTPException(status_code=404, detail="Problem not found")
    
    # Create framework
    db_framework = models.Framework(
        problem_id=problem_id,
        title=framework.title,
        content=framework.content
    )
    db.add(db_framework)
    db.commit()
    db.refresh(db_framework)
    return db_framework

@router.get("/{problem_id}/frameworks", response_model=List[schemas.Framework])
def read_problem_frameworks(problem_id: int, db: Session = Depends(database.get_db)):
    # Check if problem exists
    db_problem = db.query(models.Problem).filter(models.Problem.problem_id == problem_id).first()
    if db_problem is None:
        raise HTTPException(status_code=404, detail="Problem not found")
    
    frameworks = db.query(models.Framework).filter(models.Framework.problem_id == problem_id).all()
    return frameworks

@router.get("/frameworks/{framework_id}", response_model=schemas.Framework)
def read_framework(framework_id: int, db: Session = Depends(database.get_db)):
    db_framework = db.query(models.Framework).filter(models.Framework.framework_id == framework_id).first()
    if db_framework is None:
        raise HTTPException(status_code=404, detail="Framework not found")
    return db_framework 