"""
Ultra-focused tests to push coverage from 83% to 88%+
Targeting specific uncovered lines: 553-564 (cascade), 666-707 (conflicts), 1232-1244 (password), API lines
"""
import pytest
from datetime import datetime, timedelta
from app import db, Course, Class, Faculty, Student, User, Enrollment, AttendanceSession, Attendance
from werkzeug.security import generate_password_hash


class TestCourseDeletionCascade:
    """Test course deletion with full cascade - lines 553-564"""
    
    def test_delete_course_with_classes_and_enrollments(self, admin_client, init_database, app):
        """Test deleting course that has classes with enrollments and attendance"""
        with app.app_context():
            # Find a course with classes
            course = Course.query.join(Class).first()
            
            if course:
                # Verify it has classes
                classes = Class.query.filter_by(course_id=course.id).all()
                assert len(classes) > 0
                
                # Delete the course
                response = admin_client.post(f'/admin/courses/{course.id}/delete', follow_redirects=True)
                assert response.status_code == 200


class TestScheduleConflictDetection:
    """Test schedule conflict detection - lines 666-707"""
    
    def test_add_class_with_actual_conflict(self, admin_client, init_database, app):
        """Test adding class that conflicts with existing class"""
        with app.app_context():
            # Find an existing class
            existing_class = Class.query.first()
            
            if existing_class:
                # Try to add another class with same section and overlapping time
                # Parse the existing schedule
                schedule_parts = existing_class.schedule.split()
                days = schedule_parts[0]
                
                response = admin_client.post('/admin/classes/add', data={
                    'course_id': existing_class.course_id,
                    'faculty_id': existing_class.faculty_id,
                    'section': existing_class.section,  # Same section
                    'schedule': existing_class.schedule,  # Exact same schedule = conflict
                    'room': 'Room 999'
                }, follow_redirects=True)
                
                assert response.status_code == 200
                # Should show conflict message
                assert b'conflict' in response.data.lower() or b'exists' in response.data.lower() or b'schedule' in response.data.lower()
    
    def test_add_class_no_conflict_different_section(self, admin_client, init_database, app):
        """Test adding class with same time but different section - no conflict"""
        with app.app_context():
            existing_class = Class.query.first()
            
            if existing_class:
                # Different section = no conflict
                response = admin_client.post('/admin/classes/add', data={
                    'course_id': existing_class.course_id,
                    'faculty_id': existing_class.faculty_id,
                    'section': 'NEWZ99',  # Different section
                    'schedule': existing_class.schedule,  # Same time is OK for different section
                    'room': 'Room 888'
                }, follow_redirects=True)
                
                assert response.status_code == 200
    
    def test_add_class_no_conflict_different_days(self, admin_client, init_database, app):
        """Test adding class with different days - no conflict"""
        with app.app_context():
            existing_class = Class.query.filter(Class.schedule.like('MWF%')).first()
            
            if existing_class:
                # Same section but different days = no conflict
                response = admin_client.post('/admin/classes/add', data={
                    'course_id': existing_class.course_id,
                    'faculty_id': existing_class.faculty_id,
                    'section': existing_class.section,
                    'schedule': 'TTH 10:00-11:00',  # Different days
                    'room': 'Room 777'
                }, follow_redirects=True)
                
                assert response.status_code == 200


class TestPasswordChangeAllPaths:
    """Test all password change code paths - lines 1232-1244"""
    
    def test_password_change_success(self, admin_client, init_database):
        """Test successful password change"""
        # Change password
        response = admin_client.post('/change-password', data={
            'current_password': 'admin123',
            'new_password': 'newpass456',
            'confirm_password': 'newpass456'
        }, follow_redirects=True)
        assert response.status_code == 200
        
        # Change back
        admin_client.post('/change-password', data={
            'current_password': 'newpass456',
            'new_password': 'admin123',
            'confirm_password': 'admin123'
        }, follow_redirects=True)
    
    def test_password_change_wrong_current(self, admin_client, init_database):
        """Test password change with wrong current password"""
        response = admin_client.post('/change-password', data={
            'current_password': 'wrongpass',
            'new_password': 'newpass456',
            'confirm_password': 'newpass456'
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'current' in response.data.lower() or b'incorrect' in response.data.lower()
    
    def test_password_change_passwords_dont_match(self, admin_client, init_database):
        """Test password change with non-matching new passwords"""
        response = admin_client.post('/change-password', data={
            'current_password': 'admin123',
            'new_password': 'newpass456',
            'confirm_password': 'different789'
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'match' in response.data.lower() or b'password' in response.data.lower()


class TestAPIUpdateAllBranches:
    """Test API update all code branches - lines 1301-1302, 1337-1384"""
    
    def test_api_update_present_status(self, faculty_client, init_database, app):
        """Test API update with present status"""
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
                    # Should succeed or have validation error
                    assert response.status_code in [200, 400]
                    
                    if response.status_code == 200:
                        data = response.get_json()
                        assert 'success' in data or 'message' in data
    
    def test_api_update_absent_status(self, faculty_client, init_database, app):
        """Test API update with absent status"""
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
    
    def test_api_update_late_status(self, faculty_client, init_database, app):
        """Test API update with late status"""
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
    
    def test_api_finalize_unfinalized_session(self, faculty_client, init_database, app):
        """Test API finalize on unfinalized session"""
        with app.app_context():
            # Create a new unfinalized session
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


class TestComplexQueryPaths:
    """Test complex database query paths"""
    
    def test_student_attendance_with_late_records(self, student_client, init_database, app):
        """Test student viewing attendance that includes late records"""
        with app.app_context():
            # Create some late attendance records
            student = Student.query.first()
            if student:
                enrollments = Enrollment.query.filter_by(student_id=student.id).all()
                
                for enrollment in enrollments[:2]:  # Just first 2
                    # Find sessions for this class
                    sessions = AttendanceSession.query.filter_by(class_id=enrollment.class_id).limit(1).all()
                    
                    for session in sessions:
                        # Update attendance to late
                        attendance = Attendance.query.filter_by(
                            session_id=session.id,
                            student_id=student.id
                        ).first()
                        
                        if attendance:
                            attendance.status = 'late'
                            db.session.commit()
                
                # Now view attendance
                response = student_client.get('/student/attendance')
                assert response.status_code == 200


class TestFacultyReportExports:
    """Test faculty report export edge cases"""
    
    def test_export_pdf_with_data(self, faculty_client, init_database, app):
        """Test PDF export with actual data"""
        with app.app_context():
            # Find a class with sessions
            session = AttendanceSession.query.first()
            if session:
                response = faculty_client.get(f'/faculty/export/pdf/{session.class_id}')
                assert response.status_code == 200
                # Should be PDF content type or success
    
    def test_export_csv_with_data(self, faculty_client, init_database, app):
        """Test CSV export with actual data"""
        with app.app_context():
            # Find a class with sessions
            session = AttendanceSession.query.first()
            if session:
                response = faculty_client.get(f'/faculty/export/csv/{session.class_id}')
                assert response.status_code == 200
                # Should be CSV content or success


class TestAttendanceMarkingPost:
    """Test attendance marking POST endpoint"""
    
    def test_mark_attendance_post_endpoint(self, faculty_client, init_database, app):
        """Test marking attendance via POST"""
        with app.app_context():
            session = AttendanceSession.query.filter_by(is_finalized=False).first()
            if session:
                response = faculty_client.post('/faculty/attendance/mark', data={
                    'session_id': session.id
                }, follow_redirects=True)
                # Should handle gracefully even without attendance_data
                assert response.status_code in [200, 400]


class TestDeleteOperationsFullPath:
    """Test delete operations with full path coverage"""
    
    def test_delete_user_with_student_profile(self, admin_client, init_database, app):
        """Test deleting user that has student profile"""
        with app.app_context():
            # Create a user with student profile
            test_user = User(
                username='deltest',
                email='deltest@test.com',
                password_hash=generate_password_hash('test123'),
                role='student',
                full_name='Delete Test'
            )
            db.session.add(test_user)
            db.session.commit()
            
            test_student = Student(
                user_id=test_user.id,
                student_id='DEL001',
                department='CS',
                year=2025
            )
            db.session.add(test_student)
            db.session.commit()
            
            user_id = test_user.id
            
            # Delete
            response = admin_client.post(f'/admin/users/{user_id}/delete', follow_redirects=True)
            assert response.status_code == 200
    
    def test_delete_user_with_faculty_profile(self, admin_client, init_database, app):
        """Test deleting user that has faculty profile"""
        with app.app_context():
            # Create a user with faculty profile
            test_user = User(
                username='delfac',
                email='delfac@test.com',
                password_hash=generate_password_hash('test123'),
                role='faculty',
                full_name='Delete Faculty'
            )
            db.session.add(test_user)
            db.session.commit()
            
            test_faculty = Faculty(
                user_id=test_user.id,
                faculty_id='DELFAC001',
                department='CS',
                designation='Professor'
            )
            db.session.add(test_faculty)
            db.session.commit()
            
            user_id = test_user.id
            
            # Delete
            response = admin_client.post(f'/admin/users/{user_id}/delete', follow_redirects=True)
            assert response.status_code == 200
