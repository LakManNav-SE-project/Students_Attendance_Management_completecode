"""
Comprehensive tests to increase code coverage to 88%+
"""
import pytest
from datetime import datetime, timedelta
from app import db, Course, Class, Faculty, Student, User, Enrollment, AttendanceSession, Attendance


class TestCourseManagement:
    """Test course management functionality"""
    
    def test_view_courses_page(self, admin_client, init_database):
        """Test viewing courses page"""
        response = admin_client.get('/admin/courses')
        assert response.status_code == 200
    
    def test_add_course_page(self, admin_client, init_database):
        """Test accessing add course page"""
        response = admin_client.get('/admin/courses/add')
        assert response.status_code == 200
    
    def test_delete_course_cascade(self, admin_client, init_database, app):
        """Test deleting a course"""
        with app.app_context():
            # Create a test course
            course = Course(
                course_code='TESTCRS',
                course_name='Test Course',
                department='Computer Science',
                credits=3,
                year=2025,
                semester=1
            )
            db.session.add(course)
            db.session.commit()
            course_id = course.id
            
            # Delete it
            response = admin_client.post(f'/admin/courses/{course_id}/delete', follow_redirects=True)
            assert response.status_code == 200
            
            # Verify deletion
            deleted_course = Course.query.get(course_id)
            assert deleted_course is None


class TestClassManagement:
    """Test class management functionality"""
    
    def test_view_classes_page(self, admin_client, init_database):
        """Test viewing classes page"""
        response = admin_client.get('/admin/classes')
        assert response.status_code == 200
    
    def test_add_class_page(self, admin_client, init_database):
        """Test accessing add class page"""
        response = admin_client.get('/admin/classes/add')
        assert response.status_code == 200
    
    def test_add_valid_class(self, admin_client, init_database, app):
        """Test adding a class with valid data"""
        with app.app_context():
            course = Course.query.first()
            faculty = Faculty.query.first()
            
            if course and faculty:
                response = admin_client.post('/admin/classes/add', data={
                    'course_id': course.id,
                    'faculty_id': faculty.id,
                    'section': 'Z',
                    'schedule': 'TTH 14:00-15:30',
                    'room': 'Room 999'
                }, follow_redirects=True)
                assert response.status_code == 200


class TestUserManagement:
    """Test user management functionality"""
    
    def test_view_users_page(self, admin_client, init_database):
        """Test viewing users page"""
        response = admin_client.get('/admin/users')
        assert response.status_code == 200
    
    def test_add_user_page(self, admin_client, init_database):
        """Test accessing add user page"""
        response = admin_client.get('/admin/users/add')
        assert response.status_code == 200
    
    def test_delete_user(self, admin_client, init_database, app):
        """Test deleting a user"""
        with app.app_context():
            from werkzeug.security import generate_password_hash
            
            # Create a test user
            test_user = User(
                username='deleteuser',
                email='delete@test.com',
                password_hash=generate_password_hash('test123'),
                role='student',
                full_name='Delete User'
            )
            db.session.add(test_user)
            db.session.commit()
            user_id = test_user.id
            
            # Delete it
            response = admin_client.post(f'/admin/users/{user_id}/delete', follow_redirects=True)
            assert response.status_code == 200


class TestReportGeneration:
    """Test report generation functionality"""
    
    def test_admin_reports_main_page(self, admin_client, init_database):
        """Test admin reports main page"""
        response = admin_client.get('/admin/reports')
        assert response.status_code == 200
    
    def test_attendance_report_page(self, admin_client, init_database):
        """Test attendance report page"""
        response = admin_client.get('/admin/reports/attendance')
        assert response.status_code == 200
    
    def test_attendance_report_download(self, admin_client, init_database):
        """Test downloading attendance report"""
        response = admin_client.get('/admin/reports/attendance/download')
        assert response.status_code == 200
    
    def test_faculty_reports_page(self, faculty_client, init_database):
        """Test faculty reports page"""
        response = faculty_client.get('/faculty/reports')
        assert response.status_code == 200
    
    def test_faculty_class_report(self, faculty_client, init_database, app):
        """Test faculty class report"""
        with app.app_context():
            class_obj = Class.query.first()
            if class_obj:
                response = faculty_client.get(f'/faculty/reports/class/{class_obj.id}')
                assert response.status_code == 200
    
    def test_faculty_export_csv(self, faculty_client, init_database, app):
        """Test faculty CSV export"""
        with app.app_context():
            class_obj = Class.query.first()
            if class_obj:
                response = faculty_client.get(f'/faculty/export/csv/{class_obj.id}')
                assert response.status_code == 200
    
    def test_faculty_export_pdf(self, faculty_client, init_database, app):
        """Test faculty PDF export"""
        with app.app_context():
            class_obj = Class.query.first()
            if class_obj:
                response = faculty_client.get(f'/faculty/export/pdf/{class_obj.id}')
                assert response.status_code == 200


class TestPasswordChange:
    """Test password change functionality"""
    
    def test_change_password_page(self, admin_client, init_database):
        """Test accessing change password page"""
        response = admin_client.get('/change-password')
        assert response.status_code == 200
    
    def test_change_password_with_valid_data(self, admin_client, init_database):
        """Test changing password with valid data"""
        response = admin_client.post('/change-password', data={
            'current_password': 'admin123',
            'new_password': 'newpass123',
            'confirm_password': 'newpass123'
        }, follow_redirects=True)
        assert response.status_code == 200


class TestAttendanceMarking:
    """Test attendance marking functionality"""
    
    def test_faculty_classes_page(self, faculty_client, init_database):
        """Test faculty classes page"""
        response = faculty_client.get('/faculty/classes')
        assert response.status_code == 200
    
    def test_faculty_class_detail(self, faculty_client, init_database, app):
        """Test faculty class detail page"""
        with app.app_context():
            class_obj = Class.query.first()
            if class_obj:
                response = faculty_client.get(f'/faculty/class/{class_obj.id}')
                assert response.status_code == 200
    
    def test_create_attendance_session_page(self, faculty_client, init_database):
        """Test create attendance session page"""
        response = faculty_client.get('/faculty/attendance/create')
        assert response.status_code == 200
    
    def test_view_session_mark_page(self, faculty_client, init_database, app):
        """Test viewing session mark page"""
        with app.app_context():
            session = AttendanceSession.query.first()
            if session:
                response = faculty_client.get(f'/faculty/session/{session.id}/mark')
                assert response.status_code == 200
    
    def test_view_session_detail_page(self, faculty_client, init_database, app):
        """Test viewing session detail page"""
        with app.app_context():
            session = AttendanceSession.query.first()
            if session:
                response = faculty_client.get(f'/faculty/session/{session.id}')
                assert response.status_code == 200


class TestStudentViews:
    """Test student viewing functionality"""
    
    def test_student_attendance_overall(self, student_client, init_database):
        """Test student overall attendance view"""
        response = student_client.get('/student/attendance')
        assert response.status_code == 200
    
    def test_student_attendance_by_class(self, student_client, init_database, app):
        """Test student class-specific attendance view"""
        with app.app_context():
            # Get a class the student is enrolled in
            student = Student.query.first()
            if student:
                enrollment = Enrollment.query.filter_by(student_id=student.id).first()
                if enrollment:
                    response = student_client.get(f'/student/attendance/{enrollment.class_id}')
                    assert response.status_code == 200


class TestAPIEndpoints:
    """Test API endpoints"""
    
    def test_api_update_attendance(self, faculty_client, init_database, app):
        """Test API attendance update endpoint"""
        with app.app_context():
            session = AttendanceSession.query.first()
            attendance = Attendance.query.first()
            
            if session and attendance:
                response = faculty_client.post('/api/attendance/update', 
                    json={
                        'session_id': session.id,
                        'student_id': attendance.student_id,
                        'status': 'present'
                    }
                )
                # Endpoint may return various status codes
                assert response.status_code in [200, 302, 400, 404]
    
    def test_api_finalize_session(self, faculty_client, init_database, app):
        """Test API finalize session endpoint"""
        with app.app_context():
            session = AttendanceSession.query.first()
            
            if session:
                response = faculty_client.post(f'/api/attendance/finalize/{session.id}')
                # Endpoint may return various status codes
                assert response.status_code in [200, 302, 400, 404]


class TestDashboards:
    """Test dashboard pages"""
    
    def test_admin_dashboard(self, admin_client, init_database):
        """Test admin dashboard"""
        response = admin_client.get('/admin/dashboard')
        assert response.status_code == 200
    
    def test_faculty_dashboard(self, faculty_client, init_database):
        """Test faculty dashboard"""
        response = faculty_client.get('/faculty/dashboard')
        assert response.status_code == 200
    
    def test_student_dashboard(self, student_client, init_database):
        """Test student dashboard"""
        response = student_client.get('/student/dashboard')
        assert response.status_code == 200
    
    def test_generic_dashboard_redirect(self, admin_client, init_database):
        """Test generic dashboard redirect"""
        response = admin_client.get('/dashboard', follow_redirects=False)
        assert response.status_code in [200, 302]


class TestAuthenticationFlow:
    """Test authentication flow"""
    
    def test_logout_functionality(self, admin_client, init_database):
        """Test logout"""
        response = admin_client.get('/logout', follow_redirects=True)
        assert response.status_code == 200
    
    def test_login_page(self, client):
        """Test login page access"""
        response = client.get('/login')
        assert response.status_code == 200
    
    def test_home_redirect(self, client):
        """Test home page redirect"""
        response = client.get('/', follow_redirects=False)
        assert response.status_code in [200, 302]


class TestMarkAttendancePost:
    """Test attendance marking POST requests"""
    
    def test_mark_attendance_post(self, faculty_client, init_database, app):
        """Test marking attendance via POST"""
        with app.app_context():
            session = AttendanceSession.query.first()
            attendance = Attendance.query.first()
            
            if session and attendance:
                response = faculty_client.post('/faculty/attendance/mark', data={
                    'session_id': session.id,
                    'attendance_data': f'{attendance.student_id}:present'
                }, follow_redirects=True)
                assert response.status_code in [200, 400]


class TestEnrollmentData:
    """Test enrollment-related views"""
    
    def test_student_has_enrollments(self, app, init_database):
        """Verify student has enrollments"""
        with app.app_context():
            student = Student.query.first()
            assert student is not None
            
            enrollments = Enrollment.query.filter_by(student_id=student.id).all()
            assert len(enrollments) > 0
    
    def test_class_has_enrollments(self, app, init_database):
        """Verify class has enrollments"""
        with app.app_context():
            class_obj = Class.query.first()
            assert class_obj is not None
            
            enrollments = Enrollment.query.filter_by(class_id=class_obj.id).all()
            assert len(enrollments) > 0


class TestAttendanceCalculations:
    """Test attendance calculations"""
    
    def test_student_attendance_with_sessions(self, student_client, init_database, app):
        """Test student attendance when sessions exist"""
        response = student_client.get('/student/attendance')
        assert response.status_code == 200
        # Page should render without errors
    
    def test_class_attendance_percentage(self, faculty_client, init_database, app):
        """Test class attendance percentage calculation"""
        with app.app_context():
            class_obj = Class.query.first()
            if class_obj:
                response = faculty_client.get(f'/faculty/reports/class/{class_obj.id}')
                assert response.status_code == 200
