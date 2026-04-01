"""
E-Learning Platform - Main Entry Point
"""

from app import create_app, db
from app.models import User, Course, Enrollment, Lesson

app = create_app('development')

@app.shell_context_processor
def make_shell_context():
    """Make shell context for flask shell"""
    return {'db': db, 'User': User, 'Course': Course, 'Enrollment': Enrollment, 'Lesson': Lesson}

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
