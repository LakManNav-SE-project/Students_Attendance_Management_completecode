"""
Unit tests for Admin functionality
"""
import pytest
from app import db, User, Student, Faculty, Course, Class


class TestAdminAuthentication:
    """Test admin authentication and authorization"""
    
    def test_admin_login_success(self, client, init_database):
        """Test successful admin login"""
        response = client.post('/login', data={
            'username': 'admin',
            'password': 'admin123'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Admin Dashboard' in response.data or b'dashboard' in response.data.lower()
    
    def test_admin_login_wrong_password(self, client, init_database):
        """Test admin login with wrong password"""
        response = client.post('/login', data={
            'username': 'admin',
            'password': 'wrongpassword'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        # Check we're still on login page (not redirected to dashboard)
        assert b'Login' in response.data or b'login' in response.data.lower()
    
    def test_admin_access_without_login(self, client, init_database):
        """Test accessing admin page without login"""
        response = client.get('/admin/dashboard')
        
        assert response.status_code == 302  # Redirect to login
        assert b'login' in response.data.lower() or response.location.endswith('/login')


class TestAdminDashboard:
    """Test admin dashboard functionality"""
    
    def test_admin_dashboard_access(self, admin_client):
        """Test admin can access dashboard"""
        response = admin_client.get('/admin/dashboard')
        
        assert response.status_code == 200
        assert b'Dashboard' in response.data or b'dashboard' in response.data.lower()
    
    def test_faculty_cannot_access_admin_dashboard(self, faculty_client):
        """Test faculty user cannot access admin dashboard"""
        response = faculty_client.get('/admin/dashboard')
        
        assert response.status_code in [302, 403]  # Redirect or forbidden
    
    def test_student_cannot_access_admin_dashboard(self, student_client):
        """Test student user cannot access admin dashboard"""
        response = student_client.get('/admin/dashboard')
        
        assert response.status_code in [302, 403]  # Redirect or forbidden


class TestAdminUserManagement:
    """Test admin user management operations"""
    
    def test_view_users_list(self, admin_client):
        """Test admin can view users list"""
        response = admin_client.get('/admin/users')
        
        assert response.status_code == 200
        assert b'admin' in response.data.lower()
    
    def test_add_student_user(self, admin_client, app):
        """Test admin can add new student user"""
        response = admin_client.post('/admin/users/add', data={
            'username': 'newstudent',
            'password': 'password123',
            'email': 'newstudent@test.com',
            'role': 'student',
            'full_name': 'New Student',
            'student_id': 'ST002',
            'section': 'B',
            'year': '1',
            'department': 'Computer Science'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        
        # Verify user was created
        with app.app_context():
            user = User.query.filter_by(username='newstudent').first()
            assert user is not None
            assert user.role == 'student'
            
            student = Student.query.filter_by(user_id=user.id).first()
            assert student is not None
            assert student.student_id == 'ST002'
    
    def test_add_faculty_user(self, admin_client, app):
        """Test admin can add new faculty user"""
        response = admin_client.post('/admin/users/add', data={
            'username': 'newfaculty',
            'password': 'password123',
            'email': 'newfaculty@test.com',
            'role': 'faculty',
            'full_name': 'New Faculty',
            'faculty_id': 'FAC002',
            'department': 'Mathematics',
            'designation': 'Assistant Professor'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        
        # Verify user was created
        with app.app_context():
            user = User.query.filter_by(username='newfaculty').first()
            assert user is not None
            assert user.role == 'faculty'
            
            faculty = Faculty.query.filter_by(user_id=user.id).first()
            assert faculty is not None
            assert faculty.faculty_id == 'FAC002'
    
    def test_add_duplicate_username(self, admin_client, app):
        """Test adding user with duplicate username fails"""
        response = admin_client.post('/admin/users/add', data={
            'username': 'admin',  # Already exists
            'password': 'password123',
            'email': 'another@test.com',
            'role': 'student',
            'full_name': 'Test',
            'student_id': 'ST999',
            'section': 'A',
            'year': '1',
            'department': 'Computer Science'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'already exists' in response.data.lower() or b'error' in response.data.lower()


class TestAdminCourseManagement:
    """Test admin course management operations"""
    
    def test_view_courses_list(self, admin_client):
        """Test admin can view courses list"""
        response = admin_client.get('/admin/courses')
        
        assert response.status_code == 200
        assert b'course' in response.data.lower()
    
    def test_add_course(self, admin_client, app):
        """Test admin can add new course"""
        response = admin_client.post('/admin/courses/add', data={
            'course_name': 'Algorithms',
            'course_code': 'CS201',
            'department': 'Computer Science',
            'credits': '4',
            'year': '2',
            'semester': '1'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        
        # Verify course was created
        with app.app_context():
            course = Course.query.filter_by(course_code='CS201').first()
            assert course is not None
            assert course.course_name == 'Algorithms'
            assert course.credits == 4
    
    def test_add_duplicate_course_code(self, admin_client):
        """Test adding course with duplicate code fails"""
        response = admin_client.post('/admin/courses/add', data={
            'course_name': 'Another Course',
            'course_code': 'CS101',  # Already exists
            'department': 'Computer Science',
            'credits': '3',
            'year': '1',
            'semester': '1'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'already exists' in response.data.lower() or b'error' in response.data.lower()


class TestAdminClassManagement:
    """Test admin class management operations"""
    
    def test_view_classes_list(self, admin_client):
        """Test admin can view classes list"""
        response = admin_client.get('/admin/classes')
        
        assert response.status_code == 200
        assert b'class' in response.data.lower()
    
    def test_add_class_success(self, admin_client, app):
        """Test admin can add new class"""
        with app.app_context():
            # First create another student in section B
            user = User(
                username='student2',
                password_hash='hash',
                email='student2@test.com',
                role='student',
                full_name='Student 2'
            )
            db.session.add(user)
            db.session.commit()
            
            student = Student(
                user_id=user.id,
                student_id='ST003',
                section='B',
                year=1,
                department='Computer Science'
            )
            db.session.add(student)
            
            # Get course and faculty IDs
            course = Course.query.first()
            faculty = Faculty.query.first()
            course_id = course.id
            faculty_id = faculty.id
            db.session.commit()
        
        response = admin_client.post('/admin/classes/add', data={
            'course_id': str(course_id),
            'faculty_id': str(faculty_id),
            'section': 'A'  # Use section A which has students
        }, follow_redirects=True)
        
        assert response.status_code == 200
        
        with app.app_context():
            # Should have 2 classes now (1 from init_database + 1 new)
            classes = Class.query.filter_by(section='A').all()
            assert len(classes) >= 1
    
    def test_add_class_empty_section(self, admin_client, app):
        """Test adding class for empty section is blocked"""
        with app.app_context():
            course = Course.query.first()
            faculty = Faculty.query.first()
            course_id = course.id
            faculty_id = faculty.id
        
        response = admin_client.post('/admin/classes/add', data={
            'course_id': str(course_id),
            'faculty_id': str(faculty_id),
            'section': 'Z'  # No students in this section
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'no students' in response.data.lower() or b'error' in response.data.lower()
        
        # Verify class was NOT created
        with app.app_context():
            class_obj = Class.query.filter_by(section='Z').first()
            assert class_obj is None
