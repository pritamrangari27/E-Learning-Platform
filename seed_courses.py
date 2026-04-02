"""
Seed database with dummy courses and instructors
Run this script to populate the database with test data
"""

from app import create_app, db
from app.models import User, Course, Lesson
from datetime import datetime

app = create_app('production')

with app.app_context():
    # Create dummy instructors if they don't exist
    instructors = [
        {'username': 'dr_smith', 'email': 'smith@university.edu', 'full_name': 'Dr. John Smith', 'role': 'instructor'},
        {'username': 'prof_johnson', 'email': 'johnson@university.edu', 'full_name': 'Prof. Sarah Johnson', 'role': 'instructor'},
    ]
    
    instructor_ids = []
    for instr_data in instructors:
        existing = User.query.filter_by(username=instr_data['username']).first()
        if not existing:
            instr = User(
                username=instr_data['username'],
                email=instr_data['email'],
                full_name=instr_data['full_name'],
                role=instr_data['role']
            )
            instr.set_password('password123')
            db.session.add(instr)
            print(f"✓ Created instructor: {instr_data['full_name']}")
        else:
            instr = existing
            print(f"✓ Instructor exists: {instr_data['full_name']}")
        instructor_ids.append(instr.id)
    
    db.session.commit()
    
    # Create 12 dummy courses
    courses_data = [
        {'title': 'Python for Beginners', 'description': 'Learn Python from scratch', 'category': 'Programming'},
        {'title': 'Web Development with Django', 'description': 'Build web apps with Django framework', 'category': 'Programming'},
        {'title': 'JavaScript Essentials', 'description': 'Master JavaScript fundamentals', 'category': 'Programming'},
        {'title': 'React.js Advanced', 'description': 'Advanced React patterns and hooks', 'category': 'Frontend'},
        {'title': 'Data Science with Pandas', 'description': 'Data analysis and manipulation', 'category': 'Data Science'},
        {'title': 'Machine Learning Basics', 'description': 'Introduction to ML algorithms', 'category': 'Data Science'},
        {'title': 'Database Design & SQL', 'description': 'Master relational databases', 'category': 'Database'},
        {'title': 'Cloud Computing with AWS', 'description': 'Deploy apps on AWS', 'category': 'Cloud'},
        {'title': 'Docker & Kubernetes', 'description': 'Containerization and orchestration', 'category': 'DevOps'},
        {'title': 'Git & Version Control', 'description': 'Master Git workflows', 'category': 'Tools'},
        {'title': 'API Development REST', 'description': 'Build scalable REST APIs', 'category': 'Backend'},
        {'title': 'Mobile App Development', 'description': 'React Native mobile apps', 'category': 'Mobile'},
    ]
    
    course_count = 0
    for i, course_data in enumerate(courses_data):
        existing = Course.query.filter_by(title=course_data['title']).first()
        if not existing:
            instructor_id = instructor_ids[i % len(instructor_ids)]
            course = Course(
                title=course_data['title'],
                description=course_data['description'],
                category=course_data['category'],
                instructor_id=instructor_id,
                is_active=True
            )
            db.session.add(course)
            course_count += 1
            print(f"✓ Created course: {course_data['title']}")
        else:
            print(f"✓ Course exists: {course_data['title']}")
    
    db.session.commit()
    
    print(f"\n✅ Seeding complete!")
    print(f"   • Instructors: {len(instructors)}")
    print(f"   • Courses added: {course_count}")
    print(f"   • Total courses: {Course.query.count()}")
