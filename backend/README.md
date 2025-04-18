# Consultigo Backend API

A FastAPI backend for the Consultigo application. This API provides endpoints for managing users, problems, submissions, and AI feedback.

## Features

- User management with secure authentication
- Problem creation and management
- Submission handling with AI feedback
- SQLite database with SQLAlchemy ORM
- CORS configuration for frontend development

## Project Structure

```
backend/
├── app/
│   ├── routers/
│   │   ├── auth.py
│   │   ├── users.py
│   │   ├── problems.py
│   │   └── submissions.py
│   ├── app.py
│   ├── auth.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   └── utils.py
├── main.py
└── requirements.txt
```

## Installation & Setup

1. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the development server:
```bash
python main.py
```

The API will be available at http://localhost:8000

## API Documentation

After starting the server, you can access the interactive API documentation at:
- http://localhost:8000/docs (Swagger UI)
- http://localhost:8000/redoc (ReDoc)

## Models

The API uses the following main database models:

- **User**: Manages user accounts and authentication
- **Problem**: Stores consulting case studies and guesstimates
- **ProblemExample**: Examples for problems with sample answers
- **Submission**: User submissions for problems
- **AIFeedback**: AI-generated feedback on user submissions

## Authentication

The API uses OAuth2 password flow with JWT tokens for authentication. To authenticate:

1. Get a token by sending your credentials to `/token`
2. Include the token in the Authorization header for subsequent requests:
   `Authorization: Bearer your_token_here` 