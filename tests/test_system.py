"""
Simplified System Tests for Student Attendance Management System
Tests end-to-end workflows using existing test data
"""

import pytest
from datetime import datetime, timedelta


class TestBasicWorkflows:
    """System: Basic end-to-end workflows"""
    
    def test_admin_user_management_workflow(self, client, init_database):
        """Test admin can login and view management pages"""
        
        # Admin login
        response = client.post('/login', data={
            'username': 'admin',
            'password': 'admin123'
        }, follow_redirects=True)
        assert response.status_code == 200
        
        # View users
        response = client.get('/admin/users')
        assert response.status_code == 200
        
        # View courses
        response = client.get('/admin/courses')
        assert response.status_code == 200
        
        # View classes
        response = client.get('/admin/classes')
        assert response.status_code == 200
        
        # Logout
        response = client.get('/logout', follow_redirects=True)
        assert response.status_code == 200
    
    def test_faculty_attendance_workflow(self, client, init_database, app):
        """Test faculty can login, view classes, and access attendance pages"""
        
        # Faculty login
        response = client.post('/login', data={
            'username': 'faculty1',
            'password': 'faculty123'
        }, follow_redirects=True)
        assert response.status_code == 200
        
        # View dashboard
        response = client.get('/faculty/dashboard')
        assert response.status_code == 200
        
        # View classes
        response = client.get('/faculty/classes')
        assert response.status_code == 200
        
        # View reports
        response = client.get('/faculty/reports')
        assert response.status_code == 200
        
        # Logout
        response = client.get('/logout', follow_redirects=True)
        assert response.status_code == 200
    
    def test_student_view_workflow(self, client, init_database, app):
        """Test student can login and view attendance"""
        
        with app.app_context():
            from app import Student, User
            student = Student.query.first()
            if student:
                student_user = User.query.get(student.user_id)
                username = student_user.username
            else:
                pytest.skip("No students in database")
        
        # Student login
        response = client.post('/login', data={
            'username': username,
            'password': 'student123'
        }, follow_redirects=True)
        assert response.status_code == 200
        
        # View dashboard
        response = client.get('/student/dashboard')
        assert response.status_code == 200
        
        # View attendance
        response = client.get('/student/attendance')
        assert response.status_code == 200
        
        # Logout
        response = client.get('/logout', follow_redirects=True)
        assert response.status_code == 200


class TestAccessControl:
    """System: Role-based access control"""
    
    def test_admin_cannot_access_faculty_pages(self, client, init_database):
        """Admin should not access faculty-specific pages"""
        
        client.post('/login', data={
            'username': 'admin',
            'password': 'admin123'
        })
        
        response = client.get('/faculty/dashboard')
        assert response.status_code == 302  # Redirected
    
    def test_faculty_cannot_access_admin_pages(self, client, init_database):
        """Faculty should not access admin-specific pages"""
        
        client.post('/login', data={
            'username': 'faculty1',
            'password': 'faculty123'
        })
        
        response = client.get('/admin/dashboard')
        assert response.status_code == 302  # Redirected
    
    def test_student_cannot_access_admin_pages(self, client, init_database, app):
        """Student should not access admin-specific pages"""
        
        with app.app_context():
            from app import Student, User
            student = Student.query.first()
            student_user = User.query.get(student.user_id)
            username = student_user.username
        
        client.post('/login', data={
            'username': username,
            'password': 'student123'
        })
        
        response = client.get('/admin/dashboard')
        assert response.status_code == 302  # Redirected
    
    def test_unauthenticated_access_blocked(self, client):
        """Unauthenticated users should be redirected to login"""
        
        response = client.get('/admin/dashboard')
        assert response.status_code == 302
        
        response = client.get('/faculty/dashboard')
        assert response.status_code == 302
        
        response = client.get('/student/dashboard')
        assert response.status_code == 302


class TestMultipleUserSessions:
    """System: Multiple concurrent user sessions"""
    
    def test_separate_user_sessions(self, app, init_database):
        """Test multiple users maintain separate sessions"""
        
        admin_client = app.test_client()
        faculty_client = app.test_client()
        
        # Admin login
        admin_client.post('/login', data={
            'username': 'admin',
            'password': 'admin123'
        })
        
        # Faculty login
        faculty_client.post('/login', data={
            'username': 'faculty1',
            'password': 'faculty123'
        })
        
        # Both can access their dashboards
        admin_response = admin_client.get('/admin/dashboard')
        assert admin_response.status_code == 200
        
        faculty_response = faculty_client.get('/faculty/dashboard')
        assert faculty_response.status_code == 200
        
        # Admin cannot access faculty dashboard
        admin_as_faculty = admin_client.get('/faculty/dashboard')
        assert admin_as_faculty.status_code == 302


class TestPasswordChange:
    """System: Password change functionality"""
    
    def test_user_can_change_password(self, client, init_database, app):
        """Test user can successfully change password"""
        
        with app.app_context():
            from app import Student, User
            student = Student.query.first()
            student_user = User.query.get(student.user_id)
            username = student_user.username
        
        # Login with original password
        response = client.post('/login', data={
            'username': username,
            'password': 'student123'
        }, follow_redirects=True)
        assert response.status_code == 200
        
        # Change password
        response = client.post('/change-password', data={
            'current_password': 'student123',
            'new_password': 'newpass456',
            'confirm_password': 'newpass456'
        }, follow_redirects=True)
        assert response.status_code == 200
        
        # Logout
        client.get('/logout')
        
        # Login with new password
        response = client.post('/login', data={
            'username': username,
            'password': 'newpass456'
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'Dashboard' in response.data
        
        # Restore original password for other tests
        client.post('/change-password', data={
            'current_password': 'newpass456',
            'new_password': 'student123',
            'confirm_password': 'student123'
        })


class TestDataIntegrity:
    """System: Data integrity and validation"""
    
    def test_system_has_users(self, init_database, app):
        """Verify test database has required data"""
        
        with app.app_context():
            from app import User, Student, Faculty, Course, Class
            
            users = User.query.count()
            assert users > 0
            
            students = Student.query.count()
            assert students > 0
            
            faculty = Faculty.query.count()
            assert faculty > 0
            
            courses = Course.query.count()
            assert courses > 0
            
            classes = Class.query.count()
            assert classes > 0
    
    def test_referential_integrity(self, init_database, app):
        """Test database relationships are intact"""
        
        with app.app_context():
            from app import Class, Course, Faculty, Student, User
            
            # Classes have courses
            class_obj = Class.query.first()
            if class_obj:
                assert class_obj.course is not None
                assert class_obj.faculty_id is not None
            
            # Students have users
            student = Student.query.first()
            if student:
                assert User.query.get(student.user_id) is not None
            
            # Faculty have users
            faculty = Faculty.query.first()
            if faculty:
                assert User.query.get(faculty.user_id) is not None


class TestSessionManagement:
    """System: Session timeout and management"""
    
    def test_session_timeout(self, client, init_database, app):
        """Test session expires after timeout"""
        
        # Login
        client.post('/login', data={
            'username': 'admin',
            'password': 'admin123'
        })
        
        # Access should work
        response = client.get('/admin/dashboard')
        assert response.status_code == 200
        
        # Simulate timeout by manipulating session
        with client.session_transaction() as sess:
            old_time = (datetime.now() - timedelta(minutes=31)).isoformat()
            sess['last_activity'] = old_time
        
        # Access should fail
        response = client.get('/admin/dashboard', follow_redirects=False)
        assert response.status_code == 302
        assert '/login' in response.location


class TestNavigationFlow:
    """System: User navigation and page flow"""
    
    def test_admin_navigation(self, client, init_database):
        """Test admin can navigate between pages"""
        
        client.post('/login', data={
            'username': 'admin',
            'password': 'admin123'
        })
        
        # Dashboard
        response = client.get('/admin/dashboard')
        assert response.status_code == 200
        
        # Users page
        response = client.get('/admin/users')
        assert response.status_code == 200
        
        # Courses page
        response = client.get('/admin/courses')
        assert response.status_code == 200
        
        # Classes page
        response = client.get('/admin/classes')
        assert response.status_code == 200
        
        # Back to dashboard
        response = client.get('/admin/dashboard')
        assert response.status_code == 200
    
    def test_faculty_navigation(self, client, init_database):
        """Test faculty can navigate between pages"""
        
        client.post('/login', data={
            'username': 'faculty1',
            'password': 'faculty123'
        })
        
        # Dashboard
        response = client.get('/faculty/dashboard')
        assert response.status_code == 200
        
        # Classes
        response = client.get('/faculty/classes')
        assert response.status_code == 200
        
        # Reports
        response = client.get('/faculty/reports')
        assert response.status_code == 200
        
        # Back to dashboard
        response = client.get('/faculty/dashboard')
        assert response.status_code == 200
