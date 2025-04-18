from sqlalchemy.orm import Session
from . import models, utils, database
from datetime import datetime

def create_default_user(db: Session):
    # Print debugging information
    print("Checking for default user...")
    
    # Check if the default user already exists
    default_user = db.query(models.User).filter(models.User.email == "mihirnarula@gmail.com").first()
    
    # If the user doesn't exist, create it
    if not default_user:
        print("Default user not found. Creating...")
        hashed_password = utils.get_password_hash("password")
        default_user = models.User(
            username="mihirnarula",
            email="mihirnarula@gmail.com",
            password_hash=hashed_password,
            first_name="Mihir",
            last_name="Narula",
            bio="Default admin user",
            created_at=datetime.utcnow(),
            is_active=True,
            is_admin=True
        )
        db.add(default_user)
        db.commit()
        db.refresh(default_user)
        print(f"Default user created: mihirnarula@gmail.com / password (Username: {default_user.username}, ID: {default_user.user_id})")
    else:
        print(f"Default user already exists: {default_user.username} (ID: {default_user.user_id})")

def init_db():
    print("Initializing database...")
    db = next(database.get_db())
    create_default_user(db)
    print("Database initialization complete.") 