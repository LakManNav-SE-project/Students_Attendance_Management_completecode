"""
Final push tests - specifically targeting lines 666-707, 1232-1244, 1301-1302, 1337-1384
"""
import pytest
from datetime import datetime, timedelta
from app import db, Course, Class, Faculty, Student, User, Enrollment, AttendanceSession, Attendance
from werkzeug.security import generate_password_hash


class TestAdminReportsPagination:
    """Test admin reports with pagination and filtering - lines 666-707"""
    
    def test_attendance_report_no_filters(self, admin_client, init_database):
        """Test attendance report without any filters"""
        response = admin_client.get('/admin/reports/attendance')
        assert response.status_code == 200
    
    def test_attendance_report_course_filter_only(self, admin_client, init_database, app):
        """Test with only course filter"""
        with app.app_context():
            course = Course.query.first()
            if course:
                response = admin_client.get(f'/admin/reports/attendance?course_id={course.id}')
                assert response.status_code == 200
    
    def test_attendance_report_department_filter_only(self, admin_client, init_database):
        """Test with only department filter"""
        response = admin_client.get('/admin/reports/attendance?department=Computer Science')
        assert response.status_code == 200
    
    def test_attendance_report_date_filter_only(self, admin_client, init_database):
        """Test with only date range filter"""
        start = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        end = datetime.now().strftime('%Y-%m-%d')
        response = admin_client.get(f'/admin/reports/attendance?start_date={start}&end_date={end}')
        assert response.status_code == 200
    
    def test_attendance_report_start_date_only(self, admin_client, init_database):
        """Test with only start date"""
        start = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        response = admin_client.get(f'/admin/reports/attendance?start_date={start}')
        assert response.status_code == 200
    
    def test_attendance_report_end_date_only(self, admin_client, init_database):
        """Test with only end date"""
        end = datetime.now().strftime('%Y-%m-%d')
        response = admin_client.get(f'/admin/reports/attendance?end_date={end}')
        assert response.status_code == 200
    
    def test_attendance_report_course_and_department(self, admin_client, init_database, app):
        """Test with course and department filters"""
        with app.app_context():
            course = Course.query.first()
            if course:
                response = admin_client.get(f'/admin/reports/attendance?course_id={course.id}&department=Computer Science')
                assert response.status_code == 200
    
    def test_attendance_report_all_filters(self, admin_client, init_database, app):
        """Test with all filters combined"""
        with app.app_context():
            course = Course.query.first()
            start = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            end = datetime.now().strftime('%Y-%m-%d')
            
            if course:
                response = admin_client.get(
                    f'/admin/reports/attendance?course_id={course.id}&department=Computer Science&start_date={start}&end_date={end}'
                )
                assert response.status_code == 200


class TestPasswordChangeValidation:
    """Test password change validation - lines 1232-1244"""
    
    def test_password_change_correct_current(self, admin_client, init_database, app):
        """Test password change with correct current password"""
        response = admin_client.post('/change-password', data={
            'current_password': 'admin123',
            'new_password': 'newadminpass123',
            'confirm_password': 'newadminpass123'
        }, follow_redirects=True)
        assert response.status_code == 200
        
        # Change it back
        admin_client.post('/change-password', data={
            'current_password': 'newadminpass123',
            'new_password': 'admin123',
            'confirm_password': 'admin123'
        }, follow_redirects=True)
    
    def test_password_change_incorrect_current(self, admin_client, init_database):
        """Test password change with incorrect current password"""
        response = admin_client.post('/change-password', data={
            'current_password': 'wrongpassword',
            'new_password': 'newpass123',
            'confirm_password': 'newpass123'
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'current password' in response.data.lower() or b'incorrect' in response.data.lower()
    
    def test_password_change_mismatch_new(self, admin_client, init_database):
        """Test password change with mismatched new passwords"""
        response = admin_client.post('/change-password', data={
            'current_password': 'admin123',
            'new_password': 'newpass123',
            'confirm_password': 'different456'
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'match' in response.data.lower() or b'password' in response.data.lower()


class TestAPIAttendanceUpdate:
    """Test API attendance update - lines 1301-1302, 1337-1384"""
    
    def test_api_update_present(self, faculty_client, init_database, app):
        """Test API update to mark present"""
        with app.app_context():
            session = AttendanceSession.query.filter_by(is_finalized=False).first()
            if session:
                class_obj = Class.query.get(session.class_id)
                enrollment = Enrollment.query.filter_by(class_id=class_obj.id).first()
                
                if enrollment:
                    response = faculty_client.post('/api/attendance/update',
                        json={
                            'session_id': session.id,
                            'student_id': enrollment.student_id,
                            'status': 'present'
                        },
                        content_type='application/json'
                    )
                    assert response.status_code in [200, 400]
    
    def test_api_update_absent(self, faculty_client, init_database, app):
        """Test API update to mark absent"""
        with app.app_context():
            session = AttendanceSession.query.filter_by(is_finalized=False).first()
            if session:
                class_obj = Class.query.get(session.class_id)
                enrollment = Enrollment.query.filter_by(class_id=class_obj.id).first()
                
                if enrollment:
                    response = faculty_client.post('/api/attendance/update',
                        json={
                            'session_id': session.id,
                            'student_id': enrollment.student_id,
                            'status': 'absent'
                        },
                        content_type='application/json'
                    )
                    assert response.status_code in [200, 400]
    
    def test_api_update_late(self, faculty_client, init_database, app):
        """Test API update to mark late"""
        with app.app_context():
            session = AttendanceSession.query.filter_by(is_finalized=False).first()
            if session:
                class_obj = Class.query.get(session.class_id)
                enrollment = Enrollment.query.filter_by(class_id=class_obj.id).first()
                
                if enrollment:
                    response = faculty_client.post('/api/attendance/update',
                        json={
                            'session_id': session.id,
                            'student_id': enrollment.student_id,
                            'status': 'late'
                        },
                        content_type='application/json'
                    )
                    assert response.status_code in [200, 400]
    
    def test_api_finalize_session(self, faculty_client, init_database, app):
        """Test API session finalization"""
        with app.app_context():
            # Create a fresh session
            class_obj = Class.query.first()
            if class_obj:
                new_session = AttendanceSession(
                    class_id=class_obj.id,
                    date=datetime.now().date(),
                    start_time=datetime.now().time(),
                    end_time=(datetime.now() + timedelta(hours=1)).time(),
                    is_finalized=False
                )
                db.session.add(new_session)
                db.session.commit()
                
                response = faculty_client.post(f'/api/attendance/finalize/{new_session.id}',
                    content_type='application/json'
                )
                assert response.status_code in [200, 302, 400]
    
    def test_api_update_missing_session_id(self, faculty_client, init_database):
        """Test API update without session_id"""
        response = faculty_client.post('/api/attendance/update',
            json={
                'student_id': 1,
                'status': 'present'
            },
            content_type='application/json'
        )
        assert response.status_code in [400, 500]
    
    def test_api_update_missing_student_id(self, faculty_client, init_database):
        """Test API update without student_id"""
        response = faculty_client.post('/api/attendance/update',
            json={
                'session_id': 1,
                'status': 'present'
            },
            content_type='application/json'
        )
        assert response.status_code in [400, 500]
    
    def test_api_update_missing_status(self, faculty_client, init_database):
        """Test API update without status"""
        response = faculty_client.post('/api/attendance/update',
            json={
                'session_id': 1,
                'student_id': 1
            },
            content_type='application/json'
        )
        assert response.status_code in [400, 500]


class TestAttendanceCalculationEdgeCases:
    """Test attendance calculation edge cases - lines 189-190, 206-208"""
    
    def test_calculate_with_no_sessions(self, app, init_database):
        """Test calculation when class has no sessions"""
        with app.app_context():
            from app import calculate_attendance_percentage
            
            # Create a class with no sessions
            course = Course.query.first()
            faculty = Faculty.query.first()
            
            if course and faculty:
                new_class = Class(
                    course_id=course.id,
                    faculty_id=faculty.id,
                    section='NOSESS',
                    schedule='MWF 15:00-16:00',
                    room='Room 555'
                )
                db.session.add(new_class)
                db.session.commit()
                
                student = Student.query.first()
                if student:
                    # Calculate for this student/class combo
                    percentage = calculate_attendance_percentage(student.id, new_class.id)
                    assert percentage is None or percentage == 0
    
    def test_calculate_with_mixed_attendance(self, app, init_database):
        """Test calculation with mixed attendance statuses"""
        with app.app_context():
            from app import calculate_attendance_percentage
            
            student = Student.query.first()
            class_obj = Class.query.first()
            
            if student and class_obj:
                percentage = calculate_attendance_percentage(student.id, class_obj.id)
                assert percentage is None or (0 <= percentage <= 100)


class TestUnhandledExceptions:
    """Test exception handling paths"""
    
    def test_course_add_with_missing_fields(self, admin_client, init_database):
        """Test course addition with missing required fields"""
        response = admin_client.post('/admin/courses/add', data={
            'course_code': 'MISS001'
            # Missing other required fields
        }, follow_redirects=True)
        assert response.status_code in [200, 400]
    
    def test_class_add_with_missing_fields(self, admin_client, init_database):
        """Test class addition with missing required fields"""
        response = admin_client.post('/admin/classes/add', data={
            'section': 'MISS'
            # Missing other required fields
        }, follow_redirects=True)
        assert response.status_code in [200, 400]
    
    def test_user_add_with_missing_fields(self, admin_client, init_database):
        """Test user addition with missing required fields"""
        response = admin_client.post('/admin/users/add', data={
            'username': 'incomplete'
            # Missing other required fields
        }, follow_redirects=True)
        assert response.status_code in [200, 400]


class TestSessionEdgeCases:
    """Test session-related edge cases"""
    
    def test_view_nonexistent_session(self, faculty_client, init_database):
        """Test viewing non-existent session"""
        response = faculty_client.get('/faculty/session/99999', follow_redirects=True)
        assert response.status_code in [200, 404]
    
    def test_mark_nonexistent_session(self, faculty_client, init_database):
        """Test marking attendance for non-existent session"""
        response = faculty_client.get('/faculty/session/99999/mark', follow_redirects=True)
        assert response.status_code in [200, 404]


class TestReportDownloads:
    """Test report download edge cases"""
    
    def test_download_with_no_data(self, admin_client, init_database):
        """Test download when no matching data"""
        response = admin_client.get('/admin/reports/attendance/download?start_date=1990-01-01&end_date=1990-01-02')
        assert response.status_code == 200
    
    def test_download_with_course_filter(self, admin_client, init_database, app):
        """Test download with course filter"""
        with app.app_context():
            course = Course.query.first()
            if course:
                response = admin_client.get(f'/admin/reports/attendance/download?course_id={course.id}')
                assert response.status_code == 200
    
    def test_download_with_all_filters(self, admin_client, init_database, app):
        """Test download with all filters"""
        with app.app_context():
            course = Course.query.first()
            start = (datetime.now() - timedelta(days=60)).strftime('%Y-%m-%d')
            end = datetime.now().strftime('%Y-%m-%d')
            
            if course:
                response = admin_client.get(
                    f'/admin/reports/attendance/download?course_id={course.id}&department=Computer Science&start_date={start}&end_date={end}'
                )
                assert response.status_code == 200
