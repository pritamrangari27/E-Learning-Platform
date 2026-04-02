from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from functools import wraps
from datetime import datetime
import os
from app.models import db, User, Course, Enrollment, Lesson, student_lesson_completion

def create_app(config_name='development'):
    """
    Application factory function
    """
    # Get the base directory of the app
    base_dir = os.path.abspath(os.path.dirname(__file__))
    template_dir = os.path.join(base_dir, 'templates')
    static_dir = os.path.join(base_dir, 'static')
    
    # Project root (parent of app directory)
    project_root = os.path.dirname(base_dir)
    db_path = os.path.join(project_root, 'elearning.db')
    
    app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
    
    # Configuration
    if config_name == 'development':
        app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.config['SECRET_KEY'] = 'dev-secret-key-change-in-production'
    elif config_name == 'production':
        # For PostgreSQL in production: 'postgresql://user:password@localhost/elearning'
        app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', f'sqlite:///{db_path}')
        app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'change-me')
    
    # Initialize extensions
    db.init_app(app)
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    # ==================== Authentication Routes ====================
    
    @app.route('/register', methods=['GET', 'POST'])
    def register():
        """User registration"""
        if 'user_id' in session:
            return redirect(url_for('dashboard'))
        
        if request.method == 'POST':
            username = request.form.get('username')
            email = request.form.get('email')
            password = request.form.get('password')
            confirm_password = request.form.get('confirm_password')
            full_name = request.form.get('full_name')
            role = request.form.get('role', 'student')
            
            # Validation
            if not all([username, email, password, confirm_password, full_name]):
                flash('All fields are required', 'danger')
                return redirect(url_for('index'))
            
            if password != confirm_password:
                flash('Passwords do not match', 'danger')
                return redirect(url_for('index'))
            
            if len(password) < 6:
                flash('Password must be at least 6 characters', 'danger')
                return redirect(url_for('index'))
            
            if User.query.filter_by(username=username).first():
                flash('Username already exists', 'danger')
                return redirect(url_for('index'))
            
            if User.query.filter_by(email=email).first():
                flash('Email already registered', 'danger')
                return redirect(url_for('index'))
            
            # Create new user
            user = User(username=username, email=email, full_name=full_name, role=role)
            user.set_password(password)
            
            db.session.add(user)
            db.session.commit()
            
            flash(f'Account created successfully! Please login.', 'success')
            return redirect(url_for('login'))
        
        # Redirect to landing page with register modal (GET request)
        return redirect(url_for('index'))
    
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        """User login"""
        print(f'[LOGIN ROUTE CALLED] Method: {request.method}, Session: {bool("user_id" in session)}')
        
        if 'user_id' in session:
            print(f'[LOGIN] User already in session, redirecting to dashboard')
            return redirect(url_for('dashboard'))
        
        if request.method == 'POST':
            try:
                username = request.form.get('username')
                password = request.form.get('password')
                print(f'[LOGIN] POST - Username: {username}, Password provided: {bool(password)}')
                print(f'[LOGIN] User-Agent: {request.headers.get("User-Agent")}')
                
                user = User.query.filter_by(username=username).first()
                print(f'[LOGIN] User query result: {user.username if user else "NOT FOUND"}')
                
                if user and user.check_password(password):
                    session['user_id'] = user.id
                    session['username'] = user.username
                    session['role'] = user.role
                    flash(f'Welcome back, {user.full_name}!', 'success')
                    print(f'[LOGIN] ✓ SUCCESS for {username} - Redirecting to dashboard')
                    return redirect(url_for('dashboard'))
                else:
                    flash('Invalid username or password', 'danger')
                    print(f'[LOGIN] ✗ FAILED for {username} - Redirecting to index with error')
            except Exception as e:
                print(f'[LOGIN] ERROR: {str(e)}')
                import traceback
                traceback.print_exc()
                flash('An error occurred during login. Please try again.', 'danger')
        
        print(f'[LOGIN] GET or failed POST - Redirecting to index')
        return redirect(url_for('index'))
    
    @app.route('/logout')
    def logout():
        """User logout"""
        session.clear()
        flash('You have been logged out', 'info')
        return redirect(url_for('index'))
    
    # ==================== Decorators ====================
    
    def login_required(f):
        """Decorator to check if user is logged in"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('Please log in first', 'warning')
                return redirect(url_for('login'))
            return f(*args, **kwargs)
        return decorated_function
    
    def instructor_required(f):
        """Decorator to check if user is an instructor"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('Please log in first', 'warning')
                return redirect(url_for('login'))
            user = User.query.get(session['user_id'])
            if user.role != 'instructor':
                flash('You do not have permission to access this page', 'danger')
                return redirect(url_for('dashboard'))
            return f(*args, **kwargs)
        return decorated_function
    
    # ==================== Dashboard Routes ====================
    
    @app.route('/')
    def index():
        """Landing page"""
        if 'user_id' in session:
            return redirect(url_for('dashboard'))
        return render_template('landing.html')
    
    @app.route('/dashboard')
    @login_required
    def dashboard():
        """Main dashboard"""
        try:
            user = User.query.get(session['user_id'])
            
            if user.role == 'student':
                # Display all courses and student's enrollments
                all_courses = Course.query.filter_by(is_active=True).all()
                enrolled_courses = db.session.query(Course).join(Enrollment).filter(
                    Enrollment.student_id == user.id
                ).all()
                
                # Get list of course IDs student is already enrolled in
                enrolled_course_ids = [e.course_id for e in user.enrollments]
                
                return render_template('student_dashboard.html', 
                                     user=user, 
                                     enrolled_courses=enrolled_courses,
                                     available_courses=all_courses,
                                     enrolled_course_ids=enrolled_course_ids)
            else:  # instructor
                # Display instructor's courses
                courses = Course.query.filter_by(instructor_id=user.id).all()
                return render_template('instructor_dashboard.html', user=user, courses=courses)
        except Exception as e:
            print(f'Dashboard Error: {str(e)}')
            print(f'User Agent: {request.headers.get("User-Agent")}')
            raise
    
    # ==================== Course Routes ====================
    
    @app.route('/courses')
    @login_required
    def view_courses():
        """View all available courses"""
        try:
            courses = Course.query.filter_by(is_active=True).all()
            user = User.query.get(session['user_id'])
            
            # Get list of courses user is already enrolled in
            enrolled_course_ids = [e.course_id for e in user.enrollments]
            
            print(f'Courses Route - User: {user.username}, Courses found: {len(courses)}, User Agent: {request.headers.get("User-Agent")}')
            return render_template('courses.html', courses=courses, enrolled_course_ids=enrolled_course_ids)
        except Exception as e:
            print(f'Courses Route Error: {str(e)}')
            print(f'User Agent: {request.headers.get("User-Agent")}')
            import traceback
            traceback.print_exc()
            raise
    
    @app.route('/course/<int:course_id>')
    @login_required
    def view_course(course_id):
        """View course details"""
        try:
            course = Course.query.get_or_404(course_id)
            user = User.query.get(session['user_id'])
            enrollment = Enrollment.query.filter_by(student_id=user.id, course_id=course_id).first()
            lessons = Lesson.query.filter_by(course_id=course_id, is_active=True).order_by(Lesson.lesson_number).all()
            
            print(f'Course Detail Route - Course: {course.title}, Lessons: {len(lessons)}, User Agent: {request.headers.get("User-Agent")}')
            return render_template('course_detail.html', course=course, lessons=lessons, enrollment=enrollment)
        except Exception as e:
            print(f'Course Detail Route Error: {str(e)}')
            print(f'Course ID: {course_id}, User Agent: {request.headers.get("User-Agent")}')
            import traceback
            traceback.print_exc()
            raise
    
    @app.route('/course/create', methods=['GET', 'POST'])
    @instructor_required
    def create_course():
        """Create a new course (instructor only)"""
        if request.method == 'POST':
            title = request.form.get('title')
            description = request.form.get('description')
            category = request.form.get('category')
            
            if not all([title, description, category]):
                flash('All fields are required', 'danger')
                return redirect(url_for('dashboard'))
            
            course = Course(
                title=title,
                description=description,
                category=category,
                instructor_id=session['user_id']
            )
            
            db.session.add(course)
            db.session.commit()
            
            flash('Course created successfully!', 'success')
            return redirect(url_for('dashboard'))
        
        # For GET requests, redirect to dashboard where the modal is
        return redirect(url_for('dashboard'))
    
    # ==================== Enrollment Routes ====================
    
    @app.route('/enroll/<int:course_id>', methods=['POST'])
    @login_required
    def enroll(course_id):
        """Enroll student in a course"""
        course = Course.query.get_or_404(course_id)
        user = User.query.get(session['user_id'])
        
        # Check if already enrolled
        existing_enrollment = Enrollment.query.filter_by(
            student_id=user.id, 
            course_id=course_id
        ).first()
        
        if existing_enrollment:
            flash('You are already enrolled in this course', 'info')
        else:
            enrollment = Enrollment(student_id=user.id, course_id=course_id)
            db.session.add(enrollment)
            db.session.commit()
            flash(f'Successfully enrolled in {course.title}!', 'success')
        
        return redirect(url_for('view_course', course_id=course_id))
    
    @app.route('/unenroll/<int:course_id>', methods=['POST'])
    @login_required
    def unenroll(course_id):
        """Unenroll student from a course"""
        user = User.query.get(session['user_id'])
        enrollment = Enrollment.query.filter_by(
            student_id=user.id, 
            course_id=course_id
        ).first_or_404()
        
        db.session.delete(enrollment)
        db.session.commit()
        
        flash('You have been unenrolled from the course', 'success')
        return redirect(url_for('dashboard'))
    
    # ==================== Lesson Routes ====================
    
    @app.route('/lesson/add/<int:course_id>', methods=['GET', 'POST'])
    @instructor_required
    def add_lesson(course_id):
        """Add a new lesson to a course (instructor only)"""
        course = Course.query.get_or_404(course_id)
        
        # Verify instructor owns this course
        if course.instructor_id != session['user_id']:
            flash('You do not have permission to add lessons to this course', 'danger')
            return redirect(url_for('dashboard'))
        
        if request.method == 'POST':
            title = request.form.get('title')
            content = request.form.get('content')
            duration = request.form.get('duration_minutes', 0)
            
            if not all([title, content]):
                flash('Title and content are required', 'danger')
                return redirect(url_for('add_lesson', course_id=course_id))
            
            # Get the next lesson number
            last_lesson = Lesson.query.filter_by(course_id=course_id).order_by(Lesson.lesson_number.desc()).first()
            lesson_number = (last_lesson.lesson_number + 1) if last_lesson else 1
            
            lesson = Lesson(
                course_id=course_id,
                instructor_id=session['user_id'],
                title=title,
                content=content,
                lesson_number=lesson_number,
                duration_minutes=int(duration) if duration else 0
            )
            
            db.session.add(lesson)
            db.session.commit()
            
            flash('Lesson added successfully!', 'success')
            return redirect(url_for('view_course', course_id=course_id))
        
        return render_template('add_lesson.html', course=course)
    
    @app.route('/lesson/<int:lesson_id>')
    @login_required
    def view_lesson(lesson_id):
        """View a lesson"""
        lesson = Lesson.query.get_or_404(lesson_id)
        course = lesson.course
        user = User.query.get(session['user_id'])
        
        # Check if user is enrolled or is the instructor
        enrollment = Enrollment.query.filter_by(student_id=user.id, course_id=course.id).first()
        is_instructor = user.id == course.instructor_id
        
        if not (enrollment or is_instructor):
            flash('You do not have permission to view this lesson', 'danger')
            return redirect(url_for('dashboard'))
        
        # Mark lesson as completed if user is a student (not instructor)
        if enrollment and not is_instructor:
            # Check if lesson already completed by checking if it's in user's completed_lessons
            if lesson not in user.completed_lessons:
                # Add lesson to user's completed lessons
                user.completed_lessons.append(lesson)
                
                # Calculate and update enrollment progress
                enrollment.calculate_progress()
                
                # Commit changes
                db.session.commit()
        
        return render_template('lesson_detail.html', lesson=lesson, course=course)
    
    # ==================== Error Handlers ====================
    
    @app.errorhandler(404)
    def not_found(e):
        return render_template('404.html'), 404
    
    @app.errorhandler(500)
    def server_error(e):
        return render_template('500.html'), 500
    
    return app


if __name__ == '__main__':
    app = create_app('development')
    app.run(debug=True, host='0.0.0.0', port=5000)
