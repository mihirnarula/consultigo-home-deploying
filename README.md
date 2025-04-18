# Consultigo

A vanilla JavaScript, HTML, and CSS application for consulting case practice.

## Description

Consultigo is a comprehensive web application designed to help users practice consulting case studies, guesstimates, frameworks, and learn from examples. Built entirely with vanilla JavaScript, HTML, and CSS, this application provides a clean, modern interface for users to enhance their consulting skills.

The application features:

- Login/signup functionality
- Interactive dashboard with access to different learning modules
- Case studies with varying difficulty levels
- Guesstimates practice with solution submissions
- Consulting frameworks reference
- Examples of solved cases
- User profile with progress statistics

## Project Structure

```
consultigo-home/
└── frontend/
    ├── css/
    │   └── style.css
    ├── js/
    │   └── script.js
    ├── index.html
    ├── home.html
    ├── case-studies.html
    ├── case-detail.html
    ├── guesstimates.html
    ├── guesstimate-detail.html
    ├── examples.html
    ├── frameworks.html
    └── profile.html
```

## Features

- **Responsive Design**: Works seamlessly on desktop and mobile devices
- **Local Storage Integration**: Maintains login state and saves user solutions
- **Dynamic Navigation**: Logo click always redirects to home page when logged in
- **Interactive Case Studies**: Each case study includes a problem statement and solution input area
- **Guesstimates Practice**: Market sizing and estimation problems with workspace for calculations
- **User Profile**: Displays user information and progress statistics
- **Modern UI**: Clean, intuitive interface inspired by professional consulting platforms

## How to Use

1. Open the `frontend/index.html` file in any modern web browser
2. Log in with any email and password (for demo purposes, no actual authentication is implemented)
3. Navigate through the different sections using the cards on the home page
4. Select a case study or guesstimate to practice
5. Enter your solution in the provided text area
6. Solutions are automatically saved as you type
7. Track your progress on the profile page

## Key Improvements

- **Reorganized Structure**: All files are now in a frontend folder for better organization
- **Enhanced Navigation**: Clicking the logo always takes you to the home page
- **Detailed Problem Pages**: Case studies and guesstimates now have dedicated pages with problem statements and solution inputs
- **Persistent User Solutions**: Solutions are saved in local storage
- **No Redundant Code**: All duplicate or unnecessary code has been removed

## Technologies Used

- HTML5
- CSS3
- Vanilla JavaScript
- Local Storage API
- Google Material Icons

## Browser Compatibility

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Notes

This is a frontend-only demo. In a production environment, you would need to implement:
- Server-side authentication
- Database for storing user data and progress
- API endpoints for retrieving and updating data
- More robust validation and error handling 