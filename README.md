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

## Installation

### Prerequisites
- Python 3.8+
- pip

### Setup

1. **Create virtual environment:**
```bash
python -m venv venv
```

2. **Activate virtual environment:**
```bash
# Windows
venv\Scripts\activate

# Linux/macOS
source venv/bin/activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Run the application:**
```bash
python run.py
```

5. **Access the platform:**
Open your browser and go to `http://localhost:5000`

## Database Models

### User
- Stores student and instructor information
- Password hashing for security
- Role-based (student/instructor)

### Course
- Course title, description, category
- Linked to instructor
- Has multiple lessons and enrollments

### Enrollment
- Tracks student enrollment in courses
- Stores progress percentage (0-100)
- Marks course completion

### Lesson
- Individual lessons within courses
- Contains content and duration
- Tracks student completion

## Key Features Explained

### Progress Tracking
- When a student views a lesson, it's automatically marked as completed
- Progress is calculated: (completed_lessons / total_lessons) × 100
- Progress bar updates in real-time
- Course automatically marked as complete at 100%

### Real-Time Search
- Search courses by name, instructor, or category
- Results filter instantly as you type
- Works on dashboard and courses page

### Responsive Design
- 5-column grid layout on desktop
- Responsive breakpoints for tablets and mobile
- Smooth animations and transitions
