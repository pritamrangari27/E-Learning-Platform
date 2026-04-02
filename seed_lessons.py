"""
Seed database with dummy lessons for courses
Run this script to add lessons to all courses
"""

from app import create_app, db
from app.models import Course, Lesson

app = create_app('production')

with app.app_context():
    courses = Course.query.filter_by(is_active=True).all()
    print(f"Found {len(courses)} courses")
    
    lesson_templates = [
        {'title': 'Introduction & Setup', 'duration': 15},
        {'title': 'Core Concepts & Fundamentals', 'duration': 45},
        {'title': 'Practical Examples & Exercises', 'duration': 60},
        {'title': 'Advanced Techniques', 'duration': 50},
        {'title': 'Best Practices & Optimization', 'duration': 40},
        {'title': 'Project & Real-world Application', 'duration': 90},
    ]
    
    lessons_added = 0
    
    for course in courses:
        print(f"\n📚 Adding lessons to: {course.title}")
        
        # Check how many lessons exist
        existing_lessons = Lesson.query.filter_by(course_id=course.id).count()
        
        if existing_lessons == 0:
            # Add 6 lessons to this course
            for i, lesson_template in enumerate(lesson_templates, 1):
                lesson = Lesson(
                    course_id=course.id,
                    instructor_id=course.instructor_id,
                    title=f"{lesson_template['title']}",
                    content=f"<h3>{lesson_template['title']}</h3><p>This is lesson {i} for {course.title}. Learn about {lesson_template['title'].lower()} in this comprehensive module.</p><ul><li>Topic 1</li><li>Topic 2</li><li>Topic 3</li></ul>",
                    lesson_number=i,
                    duration_minutes=lesson_template['duration'],
                    is_active=True
                )
                db.session.add(lesson)
                lessons_added += 1
                print(f"   ✓ Lesson {i}: {lesson_template['title']} ({lesson_template['duration']} min)")
        else:
            print(f"   └─ Already has {existing_lessons} lessons, skipping")
    
    db.session.commit()
    
    print(f"\n✅ Seeding complete!")
    print(f"   • Lessons added: {lessons_added}")
    total_lessons = Lesson.query.count()
    print(f"   • Total lessons in database: {total_lessons}")
