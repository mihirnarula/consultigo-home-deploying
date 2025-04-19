from app.database import get_db
from app.models import Problem, DifficultyLevel
from datetime import datetime

def add_sample_problems():
    db = next(get_db())
    
    # Sample problems
    problems = [
        {
            "problem_id": 1,
            "title": "Market Entry Strategy",
            "description": "A luxury fashion brand is considering entering the Asian market. Develop a comprehensive market entry strategy considering cultural differences, competition, and distribution channels.",
            "difficulty": DifficultyLevel.HARD,
            "category": "Case Study",
            "estimated_time": 60,
            "author_id": 1
        },
        {
            "problem_id": 2,
            "title": "Cost Reduction Analysis",
            "description": "A manufacturing company is facing pressure to reduce costs by 20% while maintaining product quality. Analyze potential areas for cost reduction and recommend a strategy.",
            "difficulty": DifficultyLevel.MEDIUM,
            "category": "Case Study",
            "estimated_time": 45,
            "author_id": 1
        },
        {
            "problem_id": 3,
            "title": "Market Size Estimation",
            "description": "Estimate the market size for electric vehicles in the United States over the next 5 years. Consider factors such as adoption rates, government incentives, and infrastructure development.",
            "difficulty": DifficultyLevel.MEDIUM,
            "category": "Guesstimate",
            "estimated_time": 30,
            "author_id": 1
        },
        {
            "problem_id": 4,
            "title": "Revenue Estimation",
            "description": "Estimate the yearly revenue for a new premium coffee chain with 15 locations in major metropolitan areas. Consider factors like average ticket size, customer frequency, and market competition.",
            "difficulty": DifficultyLevel.MEDIUM,
            "category": "Guesstimate",
            "estimated_time": 30,
            "author_id": 1
        },
        {
            "problem_id": 5,
            "title": "Cost Structure Analysis",
            "description": "Analyze the cost structure for a subscription-based software company. Identify key cost drivers and suggest optimization strategies.",
            "difficulty": DifficultyLevel.HARD,
            "category": "Guesstimate",
            "estimated_time": 45,
            "author_id": 1
        }
    ]
    
    # Add problems to database if they don't already exist
    for problem_data in problems:
        existing = db.query(Problem).filter(Problem.problem_id == problem_data["problem_id"]).first()
        if existing:
            print(f"Problem with ID {problem_data['problem_id']} already exists: {existing.title}")
        else:
            # Create new problem
            problem = Problem(
                problem_id=problem_data["problem_id"],
                title=problem_data["title"],
                description=problem_data["description"],
                difficulty=problem_data["difficulty"],
                category=problem_data["category"],
                estimated_time=problem_data["estimated_time"],
                author_id=problem_data["author_id"],
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                is_active=True
            )
            db.add(problem)
            print(f"Created problem with ID {problem_data['problem_id']}: {problem_data['title']}")
    
    db.commit()
    print("Sample problems added successfully")

if __name__ == "__main__":
    add_sample_problems() 