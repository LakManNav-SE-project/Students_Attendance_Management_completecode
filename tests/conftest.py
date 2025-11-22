"""
Test configuration and fixtures for pytest
"""
import os
import tempfile
import pytest
from app import app as flask_app, db, AttendanceSession
from werkzeug.security import generate_password_hash


@pytest.fixture(scope='session')
def app():
    """Create application instance for testing"""
    # Set test configuration
    test_db_fd, test_db_path = tempfile.mkstemp()
    
    flask_app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': f'sqlite:///{test_db_path}',
        'WTF_CSRF_ENABLED': False,  # Disable CSRF for testing
        'SECRET_KEY': 'test-secret-key',
        'SERVER_NAME': 'localhost.localdomain'
    })
    
    # Create database and tables
    with flask_app.app_context():
        db.create_all()
        
    yield flask_app
    
    # Cleanup
    os.close(test_db_fd)
    os.unlink(test_db_path)


@pytest.fixture(scope='function')
def client(app):
    """Create test client"""
    return app.test_client()


@pytest.fixture(scope='function')
def runner(app):
    """Create test CLI runner"""
    return app.test_cli_runner()


@pytest.fixture(scope='function')
def init_database(app):
    """Initialize database with test data"""
    with app.app_context():
        # Import models
        from app import User, Student, Faculty, Course, Class, Enrollment
        
        # Clear existing data
        db.session.query(Enrollment).delete()
        db.session.query(Class).delete()
        db.session.query(Course).delete()
        db.session.query(Student).delete()
        db.session.query(Faculty).delete()
        db.session.query(User).delete()
        
        # Create admin user
        admin_user = User(
            username='admin',
            password_hash=generate_password_hash('admin123'),
            email='admin@test.com',
            role='admin',
            full_name='Admin User'
        )
        db.session.add(admin_user)
        
        # Create faculty user
        faculty_user = User(
            username='faculty1',
            password_hash=generate_password_hash('faculty123'),
            email='faculty1@test.com',
            role='faculty',
            full_name='Test Faculty'
        )
        db.session.add(faculty_user)
        
        # Create student user
        student_user = User(
            username='student1',
            password_hash=generate_password_hash('student123'),
            email='student1@test.com',
            role='student',
            full_name='Test Student'
        )
        db.session.add(student_user)
        
        db.session.commit()
        
        # Create faculty record
        faculty = Faculty(
            user_id=faculty_user.id,
            faculty_id='FAC001',
            department='Computer Science',
            designation='Professor'
        )
        db.session.add(faculty)
        
        # Create student record
        student = Student(
            user_id=student_user.id,
            student_id='ST001',
            department='Computer Science',
            year=1,
            section='A'
        )
        db.session.add(student)
        
        # Create course
        course = Course(
            course_code='CS101',
            course_name='Data Structures',
            department='Computer Science',
            credits=4,
            year=1,
            semester=1
        )
        db.session.add(course)
        
        db.session.commit()
        
        # Create class
        class_obj = Class(
            course_id=course.id,
            faculty_id=faculty.id,
            section='A'
        )
        db.session.add(class_obj)
        
        db.session.commit()
        
        # Create enrollment
        enrollment = Enrollment(
            student_id=student.id,
            class_id=class_obj.id
        )
        db.session.add(enrollment)
        db.session.commit()
        
        # Create attendance session for testing
        from datetime import date, time
        session_obj = AttendanceSession(
            class_id=class_obj.id,
            date=date.today(),
            start_time=time(9, 0),
            end_time=time(10, 0),
            created_by=faculty_user.id
        )
        db.session.add(session_obj)
        db.session.commit()
        
    yield db
    
    # Cleanup after test
    with app.app_context():
        db.session.remove()
        db.drop_all()
        db.create_all()


@pytest.fixture
def admin_client(client, init_database, app):
    """Client logged in as admin"""
    with app.app_context():
        with client.session_transaction() as sess:
            sess['user_id'] = 1  # Admin user ID
            sess['_fresh'] = True
    return client


@pytest.fixture
def faculty_client(client, init_database, app):
    """Client logged in as faculty"""
    with app.app_context():
        with client.session_transaction() as sess:
            sess['user_id'] = 2  # Faculty user ID
            sess['_fresh'] = True
    return client


@pytest.fixture
def student_client(client, init_database, app):
    """Client logged in as student"""
    with app.app_context():
        with client.session_transaction() as sess:
            sess['user_id'] = 3  # Student user ID
            sess['_fresh'] = True
    return client


@pytest.fixture
def app_context(app):
    """Provide application context"""
    with app.app_context():
        yield app


@pytest.fixture
def admin_user(app):
    """Get admin user"""
    with app.app_context():
        from app import User
        return User.query.filter_by(role='admin').first()


@pytest.fixture
def sample_faculty_user(app):
    """Get faculty user"""
    with app.app_context():
        from app import User
        return User.query.filter_by(role='faculty').first()


@pytest.fixture
def sample_student_user(app):
    """Get student user"""
    with app.app_context():
        from app import User
        return User.query.filter_by(role='student').first()


@pytest.fixture
def sample_faculty(app, init_database):
    """Get faculty record"""
    with app.app_context():
        from app import Faculty
        return Faculty.query.first()


@pytest.fixture
def sample_student(app, init_database):
    """Get student record"""
    with app.app_context():
        from app import Student
        return Student.query.first()


@pytest.fixture
def sample_course(app, init_database):
    """Get course record"""
    with app.app_context():
        from app import Course
        return Course.query.first()


@pytest.fixture
def sample_class(app, init_database):
    """Get class record"""
    with app.app_context():
        from app import Class
        return Class.query.first()
