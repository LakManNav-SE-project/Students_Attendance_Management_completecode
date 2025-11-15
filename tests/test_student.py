"""
Test Suite for Student Functionality
Tests: Viewing attendance, profile
"""
import pytest
from app import db, User, Student, Attendance, AttendanceSession


class TestStudentAuthentication:
    """Test student login and access control"""
    
    def test_student_login_success(self, client, init_database):
        """Student can login with correct credentials"""
        response = client.post('/login', data={
            'username': 'student1',
            'password': 'student123'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Student Dashboard' in response.data or b'dashboard' in response.data.lower()
    
    def test_student_cannot_access_admin_pages(self, student_client):
        """Student cannot access admin dashboard"""
        response = student_client.get('/admin/dashboard')
        assert response.status_code in [302, 403]
    
    def test_student_cannot_access_faculty_pages(self, student_client):
        """Student cannot access faculty pages"""
        response = student_client.get('/faculty/dashboard')
        assert response.status_code in [302, 403]


class TestStudentAttendanceViewing:
    """Test student viewing their attendance records"""
    
    def test_view_overall_attendance(self, student_client):
        """Student can view overall attendance dashboard"""
        response = student_client.get('/student/attendance')
        assert response.status_code == 200
    
    def test_view_class_specific_attendance(self, student_client, app):
        """Student can view attendance for specific class"""
        with app.app_context():
            student = Student.query.first()
            if student and student.enrollments:
                class_id = student.enrollments[0].class_id
                response = student_client.get(f'/student/attendance/{class_id}')
                assert response.status_code == 200


class TestStudentDashboard:
    """Test student dashboard functionality"""
    
    def test_dashboard_shows_classes(self, student_client):
        """Student dashboard displays enrolled classes"""
        response = student_client.get('/student/dashboard')
        assert response.status_code == 200
        assert b'class' in response.data.lower() or b'course' in response.data.lower()
    
    def test_dashboard_shows_attendance_percentage(self, student_client):
        """Student dashboard shows attendance percentage"""
        response = student_client.get('/student/dashboard')
        assert response.status_code == 200
        # Check for percentage symbol
        assert b'%' in response.data
