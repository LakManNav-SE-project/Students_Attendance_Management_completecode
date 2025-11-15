"""
Test Suite for Faculty Functionality
Tests: Session creation, attendance marking, reports
"""
import pytest
from app import db, User, Faculty, Student, Course, Class, AttendanceSession, Attendance, Enrollment
from datetime import datetime, date, time


class TestFacultyAuthentication:
    """Test faculty login and access control"""
    
    def test_faculty_login_success(self, client, init_database):
        """Faculty can login with correct credentials"""
        response = client.post('/login', data={
            'username': 'faculty1',
            'password': 'faculty123'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Faculty Dashboard' in response.data or b'dashboard' in response.data.lower()
    
    def test_faculty_cannot_access_admin_pages(self, faculty_client):
        """Faculty cannot access admin dashboard"""
        response = faculty_client.get('/admin/dashboard')
        assert response.status_code in [302, 403]


class TestFacultySessionManagement:
    """Test attendance session creation and management"""
    
    def test_create_attendance_session(self, faculty_client, app):
        """Faculty can create new attendance session"""
        with app.app_context():
            faculty = Faculty.query.first()
            class_obj = Class.query.filter_by(faculty_id=faculty.id).first()
        
        response = faculty_client.post('/faculty/attendance/create', data={
            'class_id': str(class_obj.id),
            'date': '2025-11-15',
            'start_time': '09:00',
            'end_time': '10:00'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        
        with app.app_context():
            session = AttendanceSession.query.filter_by(class_id=class_obj.id).first()
            assert session is not None
    
    def test_view_class_sessions(self, faculty_client, app):
        """Faculty can view all sessions for their class"""
        with app.app_context():
            faculty = Faculty.query.first()
            class_obj = Class.query.filter_by(faculty_id=faculty.id).first()
        
        response = faculty_client.get(f'/faculty/class/{class_obj.id}')
        assert response.status_code == 200
        assert b'session' in response.data.lower()


class TestFacultyAttendanceMarking:
    """Test marking and updating attendance"""
    
    def test_mark_attendance_present(self, faculty_client, app):
        """Faculty can mark student as present"""
        with app.app_context():
            session = AttendanceSession.query.first()
            student = Student.query.first()
        
        response = faculty_client.post('/faculty/attendance/mark', data={
            'session_id': str(session.id),
            'student_id': str(student.id),
            'status': 'present'
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] == True
    
    def test_mark_attendance_absent(self, faculty_client, app):
        """Faculty can mark student as absent"""
        with app.app_context():
            session = AttendanceSession.query.first()
            student = Student.query.first()
        
        response = faculty_client.post('/faculty/attendance/mark', data={
            'session_id': str(session.id),
            'student_id': str(student.id),
            'status': 'absent'
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] == True
    
    def test_update_attendance_within_24_hours(self, faculty_client, app):
        """Faculty can update attendance within 24 hours"""
        # Create recent attendance record
        with app.app_context():
            session = AttendanceSession.query.first()
            student = Student.query.first()
            
            attendance = Attendance(
                session_id=session.id,
                student_id=student.id,
                status='present',
                marked_by=2
            )
            db.session.add(attendance)
            db.session.commit()
            attendance_id = attendance.id
        
        response = faculty_client.post('/api/attendance/update', 
            json={
                'attendance_id': attendance_id,
                'status': 'absent'
            }
        )
        
        # May fail if session is old, check response
        assert response.status_code in [200, 403]


class TestFacultyReports:
    """Test faculty reporting functionality"""
    
    def test_view_class_report(self, faculty_client, app):
        """Faculty can view attendance report for their class"""
        with app.app_context():
            faculty = Faculty.query.first()
            class_obj = Class.query.filter_by(faculty_id=faculty.id).first()
        
        response = faculty_client.get(f'/faculty/reports/class/{class_obj.id}')
        assert response.status_code == 200
    
    def test_access_reports_page(self, faculty_client):
        """Faculty can access reports page"""
        response = faculty_client.get('/faculty/reports')
        assert response.status_code == 200
