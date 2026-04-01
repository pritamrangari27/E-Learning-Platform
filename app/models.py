from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

# Association table for student completed lessons (many-to-many)
student_lesson_completion = db.Table(
    'student_lesson_completion',
    db.Column('student_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('lesson_id', db.Integer, db.ForeignKey('lessons.id'), primary_key=True),
    db.Column('completed_at', db.DateTime, default=datetime.utcnow)
)

class User(db.Model):
    """
    User model representing both Students and Instructors
    """
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='student')  # 'student' or 'instructor'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    courses_created = db.relationship('Course', backref='instructor', lazy=True, foreign_keys='Course.instructor_id')
    enrollments = db.relationship('Enrollment', backref='student', lazy=True, cascade='all, delete-orphan')
    lessons = db.relationship('Lesson', backref='created_by', lazy=True, cascade='all, delete-orphan')
    completed_lessons = db.relationship('Lesson', secondary=student_lesson_completion, lazy=True)
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if provided password matches hash"""
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'


class Course(db.Model):
    """
    Course model representing available courses
    """
    __tablename__ = 'courses'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    instructor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    category = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    enrollments = db.relationship('Enrollment', backref='course', lazy=True, cascade='all, delete-orphan')
    lessons = db.relationship('Lesson', backref='course', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Course {self.title}>'


class Enrollment(db.Model):
    """
    Enrollment model representing student enrollments in courses
    """
    __tablename__ = 'enrollments'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False, index=True)
    enrolled_at = db.Column(db.DateTime, default=datetime.utcnow)
    progress = db.Column(db.Float, default=0.0)  # Percentage 0-100
    is_completed = db.Column(db.Boolean, default=False)
    completed_at = db.Column(db.DateTime, nullable=True)
    
    # Composite unique constraint to prevent duplicate enrollments
    __table_args__ = (db.UniqueConstraint('student_id', 'course_id', name='unique_enrollment'),)
    
    def calculate_progress(self):
        """Calculate progress percentage based on completed lessons in this course"""
        # Get total lessons in this course
        total_lessons = Lesson.query.filter_by(course_id=self.course_id).count()
        
        if total_lessons == 0:
            return 0.0
        
        # Count completed lessons by querying the association table directly
        from sqlalchemy import text
        
        result = db.session.execute(
            text("""
                SELECT COUNT(*) FROM student_lesson_completion slc
                INNER JOIN lessons l ON slc.lesson_id = l.id
                WHERE slc.student_id = :student_id AND l.course_id = :course_id
            """),
            {'student_id': self.student_id, 'course_id': self.course_id}
        ).scalar()
        
        completed_lessons = result if result else 0
        
        # Calculate percentage
        progress_percentage = (completed_lessons / total_lessons) * 100 if total_lessons > 0 else 0.0
        
        # Update progress field
        self.progress = progress_percentage
        
        # Mark as completed if progress is 100%
        if progress_percentage == 100.0:
            self.is_completed = True
            self.completed_at = datetime.utcnow()
        
        return progress_percentage
    
    def __repr__(self):
        return f'<Enrollment User:{self.student_id} Course:{self.course_id}>'


class Lesson(db.Model):
    """
    Lesson model representing individual lessons within courses
    """
    __tablename__ = 'lessons'
    
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False, index=True)
    instructor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    lesson_number = db.Column(db.Integer, nullable=False)  # Order of lessons
    duration_minutes = db.Column(db.Integer, default=0)  # Lesson duration in minutes
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    def __repr__(self):
        return f'<Lesson {self.title}>'
