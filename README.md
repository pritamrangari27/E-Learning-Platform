# E-Learning Platform

A modern, full-featured e-learning platform built with Flask and SQLAlchemy. Students can enroll in courses, track their progress, and learn from instructors.

## Features

### For Students
- Register and create an account
- Browse and search courses by name, instructor, or category
- Enroll in courses with one click
- Track progress with visual progress bars
- View course details including lessons and instructor information
- Real-time course search functionality

### For Instructors
- Create and manage courses
- Add lessons to courses with content and duration
- View student enrollments
- Track student progress

## Tech Stack

- **Backend**: Flask
- **Database**: SQLite with SQLAlchemy ORM
- **Frontend**: Bootstrap 5.3.0, Bootstrap Icons 1.11.0, Custom CSS
- **Authentication**: Session-based with password hashing

## Project Structure

```
E-Learning Platform/
├── app/
│   ├── __init__.py          # Flask app factory and all routes
│   ├── models.py            # Database models
│   ├── templates/           # HTML templates
│   │   ├── landing.html     # Landing/login/register page
│   │   ├── base.html        # Base template
│   │   ├── student_dashboard.html
│   │   ├── instructor_dashboard.html
│   │   ├── courses.html     # Browse all courses
│   │   └── ... (other templates)
│   └── static/              # CSS and static files
├── run.py                   # Entry point
├── requirements.txt         # Python dependencies
└── elearning.db            # SQLite database
```

Preview :

<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/0d2e21ac-098e-4eb2-bfe8-b0d24aa47bed" />

