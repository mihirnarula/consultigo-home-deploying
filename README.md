# Consultigo

A full-stack application for consulting case interview preparation with AI-powered feedback.

## Overview:

Consultigo is a comprehensive platform designed to help aspiring consultants prepare for case interviews through practice with real-world business scenarios, guesstimates, consulting frameworks, and expert examples. The application combines a clean, modern frontend with a powerful AI-driven backend to provide personalized feedback on user solutions.

## Key Features

### User Experience
- **Intuitive Dashboard**: Navigate between different practice modules from a central hub
- **Progressive Learning**: Problems with varying difficulty levels (Easy, Medium, Hard, Expert)
- **Personalized Feedback**: AI-powered evaluation with specific improvement suggestions
- **Performance Tracking**: Monitor progress and improvement over time

### Practice Modules
- **Case Studies**: Business problem scenarios requiring structured analysis
- **Guesstimates**: Market sizing and estimation questions to develop quantitative skills
- **Frameworks Library**: Reference guide to essential consulting frameworks and methodologies
- **Expert Examples**: Sample solutions demonstrating effective approaches

### Technical Features
- **Responsive Design**: Optimized layout for desktop and mobile devices
- **AI-Powered Feedback**: Google Gemini AI integration for solution evaluation
- **Secure Authentication**: JWT token-based user authentication
- **RESTful API**: Comprehensive endpoints for all application features
- **Database Integration**: Structured data storage with SQLAlchemy ORM
- **Local Storage**: Client-side solution saving and user session management

## Architecture

### Frontend
- **Technology**: Pure vanilla JavaScript, HTML5, and CSS3
- **Design Philosophy**: Clean, distraction-free interface with Material Design elements
- **Responsive Design**: Adapts to different screen sizes and orientations
- **Client-Side Storage**: Uses browser's localStorage API for session and solution persistence

### Backend
- **Web Framework**: FastAPI (Python)
- **Database**: SQLite with SQLAlchemy ORM
- **Authentication**: OAuth2 with JWT tokens
- **AI Integration**: Google Gemini 2.0 Flash API with fallback mechanisms
- **API Documentation**: Interactive Swagger UI and ReDoc interfaces

## Project Structure

```
consultigo-home/
├── frontend/
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   └── script.js
│   ├── images/
│   ├── examples/
│   ├── frameworks/
│   ├── index.html
│   ├── auth.html
│   ├── home.html
│   ├── case-studies.html
│   ├── case-detail.html
│   ├── guesstimates.html
│   ├── guesstimate-detail.html
│   ├── examples.html
│   ├── example-detail.html
│   ├── frameworks.html
│   ├── framework-detail.html
│   └── profile.html
│
├── backend/
│   ├── app/
│   │   ├── routers/
│   │   │   ├── auth.py
│   │   │   ├── users.py
│   │   │   ├── problems.py
│   │   │   └── submissions.py
│   │   ├── app.py
│   │   ├── auth.py
│   │   ├── database.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── utils.py
│   │   └── initial_data.py
│   ├── main.py
│   ├── consultigo.db
│   ├── add_sample_problems.py
│   ├── update_database.py
│   ├── run_setup.py
│   └── requirements.txt
│
└── README.md
```

## Database Models

### User
- User account information (username, email, password hash)
- Profile details (first/last name, bio, profile picture)
- Authentication status (is_active, is_admin)

### Problem
- Problem details (title, description, category)
- Metadata (difficulty level, estimated completion time)
- Relationships to examples, frameworks, and submissions

### ProblemExample
- Example case solutions for reference
- Associated with specific problems

### Framework
- Consulting frameworks and methodologies
- Structured content for learning reference

### Submission
- User solutions to problems
- Processing status tracking
- Connection to feedback

### AIFeedback
- AI-generated evaluation of submissions
- Detailed scoring across multiple dimensions:
  - Overall solution quality
  - Structure and organization
  - Assumptions quality/clarity
  - Analysis quality/math accuracy
  - Communication effectiveness

## Installation and Setup

### Frontend
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/consultigo-home.git
   cd consultigo-home
   ```

2. Open the frontend in your browser:
   ```bash
   cd frontend
   # Use any local development server or simply open index.html in a browser
   ```

3. For development with live reload, you can use any simple HTTP server:
   ```bash
   # Using Python's built-in HTTP server
   python -m http.server
   
   # Or with Node.js's http-server
   npx http-server
   ```

### Backend
1. Create and activate a virtual environment:
   ```bash
   cd backend
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Initialize the database:
   ```bash
   python run_setup.py
   ```

4. Start the server:
   ```bash
   python main.py
   ```

5. The API will be available at http://localhost:8000

## API Endpoints

### Authentication
- `POST /token`: Obtain a JWT token with email/password
- `GET /users/me`: Get current user information

### Users
- `POST /users/`: Create a new user account
- `GET /users/{user_id}`: Retrieve user information
- `PUT /users/{user_id}`: Update user information

### Problems
- `GET /problems/`: List all problems
- `GET /problems/{problem_id}`: Get a specific problem
- `POST /problems/`: Create a new problem (admin only)
- `GET /problems/{problem_id}/examples`: Get examples for a problem

### Submissions
- `POST /submissions/`: Create a new submission
- `GET /submissions/`: List submissions (filtered by user or problem)
- `GET /submissions/{submission_id}`: Get a specific submission
- `PUT /submissions/{submission_id}`: Update a submission
- `POST /submissions/{problem_id}/submit`: Submit a solution for AI feedback
- `GET /submissions/{submission_id}/feedback`: Get AI feedback for a submission

## User Flow

1. **Authentication**: User signs up or logs in to access the platform
2. **Dashboard**: From the home page, user selects a practice module (Case Studies, Guesstimates, Frameworks, or Examples)
3. **Selection**: User browses available problems/content and selects an item
4. **Practice**: For case studies and guesstimates:
   - User reads the problem statement
   - User develops and types their solution
   - Solution is automatically saved as they type
5. **Feedback**: User submits their solution for AI evaluation
   - System processes submission using Google Gemini AI
   - User receives detailed feedback with scores and improvement suggestions
6. **Learning**: For frameworks and examples:
   - User studies the provided content
   - User can reference this material when working on case studies and guesstimates
7. **Progress Tracking**: User can view their submission history and performance statistics in their profile

## AI Integration

### Google Gemini 2.0 Flash
- **Implementation**: API integration with the Gemini generative AI model
- **Purpose**: Evaluate user solutions and provide expert-quality feedback
- **Prompting Strategy**: Structured prompts that guide the AI to analyze:
  - Solution structure and organization
  - Quality of assumptions
  - Analytical depth and accuracy
  - Communication clarity and effectiveness
- **Fallback Mechanism**: Local mock feedback generation when API calls fail

### Feedback Format
- **Overall Score**: Numerical evaluation (1-10) of solution quality
- **Dimension Scores**: Detailed scoring across specific skill areas
- **Strengths Analysis**: Identification of effective elements in the solution
- **Improvement Areas**: Specific suggestions for enhancing the solution
- **Final Assessment**: Summary evaluation with actionable guidance

## Technologies Used

### Frontend
- HTML5
- CSS3
- Vanilla JavaScript (ES6+)
- Local Storage API
- Google Material Icons
- Responsive design techniques

### Backend
- Python 3.9+
- FastAPI framework
- SQLAlchemy ORM
- JWT authentication
- SQLite database
- Google Gemini AI API
- Pydantic data validation

## Deployment Considerations

The current implementation is designed for local development. For production deployment, consider:

1. **Database**: Migrate to a production database (PostgreSQL, MySQL)
2. **Authentication**: Implement more robust security measures
3. **Frontend Hosting**: Deploy static assets to a CDN
4. **Backend Hosting**: Use a production-grade ASGI server (Uvicorn, Hypercorn)
5. **Environment Variables**: Secure storage of API keys and credentials
6. **Monitoring**: Implement logging and performance monitoring
7. **HTTPS**: Enable secure connections
8. **Rate Limiting**: Protect API endpoints from abuse

## Browser Compatibility

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Contributing

Contributions to Consultigo are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the Mihir License - see the LICENSE file for details.

## Contact

Your Name - mihirnarula@example.com
Project Link: https://github.com/mihirnarula/consultigo-home 