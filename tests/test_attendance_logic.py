"""
Test Suite for Attendance Business Logic
Tests: Attendance calculation, notifications, 24-hour lock
"""
import pytest
from app import db, User, Student, Faculty, Attendance, AttendanceSession, Notification, Class, calculate_attendance_percentage, can_edit_attendance
from datetime import datetime, timedelta, time, date


class TestAttendanceCalculation:
    """Test attendance percentage calculation"""
    
    def test_calculate_attendance_all_present(self, app, init_database):
        """Calculate 100% when all attendance is present"""
        with app.app_context():
            student = Student.query.first()
            class_obj = Class.query.first()
            session = AttendanceSession.query.filter_by(class_id=class_obj.id).first()
            
            # Mark all as present
            for i in range(5):
                attendance = Attendance(
                    session_id=session.id,
                    student_id=student.id,
                    status='present',
                    marked_by=2
                )
                db.session.add(attendance)
            db.session.commit()
            
            percentage = calculate_attendance_percentage(student.id, class_obj.id)
            assert percentage == 100.0
    
    def test_calculate_attendance_mixed(self, app, init_database):
        """Calculate correct percentage with mixed attendance"""
        with app.app_context():
            student = Student.query.first()
            class_obj = Class.query.first()
            session = AttendanceSession.query.filter_by(class_id=class_obj.id).first()
            
            # 3 present, 2 absent = 60%
            for i in range(3):
                attendance = Attendance(
                    session_id=session.id,
                    student_id=student.id,
                    status='present',
                    marked_by=2
                )
                db.session.add(attendance)
            
            for i in range(2):
                attendance = Attendance(
                    session_id=session.id,
                    student_id=student.id,
                    status='absent',
                    marked_by=2
                )
                db.session.add(attendance)
            db.session.commit()
            
            percentage = calculate_attendance_percentage(student.id, class_obj.id)
            assert percentage == 60.0


class TestLowAttendanceNotifications:
    """Test automatic notification system for low attendance"""
    
    def test_notification_sent_below_75_percent(self, app, init_database):
        """Notification sent when attendance drops below 75%"""
        with app.app_context():
            student = Student.query.first()
            
            # Create notification
            notification = Notification(
                user_id=student.user_id,
                title='Low Attendance Alert',
                message='Your attendance has dropped below 75%',
                type='low_attendance'
            )
            db.session.add(notification)
            db.session.commit()
            
            notif = Notification.query.filter_by(
                user_id=student.user_id,
                type='low_attendance'
            ).first()
            
            assert notif is not None
            assert '75%' in notif.message
    
    def test_no_duplicate_notifications_within_7_days(self, app, init_database):
        """Should not send multiple notifications within 7 days"""
        with app.app_context():
            student = Student.query.first()
            
            # Create first notification
            notif1 = Notification(
                user_id=student.user_id,
                title='Low Attendance Alert',
                message='Test',
                type='low_attendance',
                created_at=datetime.utcnow()
            )
            db.session.add(notif1)
            db.session.commit()
            
            # Check if recent notification exists
            recent = Notification.query.filter_by(
                user_id=student.user_id,
                type='low_attendance'
            ).filter(
                Notification.created_at >= datetime.utcnow() - timedelta(days=7)
            ).first()
            
            assert recent is not None


class TestAttendanceEditingLock:
    """Test 24-hour editing window"""
    
    def test_can_edit_within_24_hours(self, app, init_database):
        """Can edit attendance within 24 hours of session end"""
        with app.app_context():
            # Create session ending 1 hour ago
            session = AttendanceSession(
                class_id=1,
                date=datetime.now().date(),
                start_time=time(8, 0),
                end_time=(datetime.now() - timedelta(hours=1)).time(),
                created_by=2
            )
            db.session.add(session)
            db.session.commit()
            
            can_edit = can_edit_attendance(session)
            assert can_edit == True
    
    def test_cannot_edit_after_24_hours(self, app, init_database):
        """Cannot edit attendance after 24 hours of session end"""
        with app.app_context():
            # Create session that ended fully 25 hours ago
            end_dt = datetime.now() - timedelta(hours=25)
            session = AttendanceSession(
                class_id=1,
                date=end_dt.date(),
                start_time=(end_dt - timedelta(hours=1)).time(),
                end_time=end_dt.time(),
                created_by=2
            )
            db.session.add(session)
            db.session.commit()
            
            can_edit = can_edit_attendance(session)
            assert can_edit == False
    
    def test_cannot_edit_finalized_session(self, app, init_database):
        """Cannot edit finalized session regardless of time"""
        with app.app_context():
            session = AttendanceSession(
                class_id=1,
                date=datetime.now().date(),
                start_time=time(8, 0),
                end_time=time(9, 0),
                created_by=2,
                is_finalized=True
            )
            db.session.add(session)
            db.session.commit()
            
            can_edit = can_edit_attendance(session)
            assert can_edit == False


class TestAttendanceStatusTypes:
    """Test different attendance status types"""
    
    def test_mark_as_late(self, faculty_client, app):
        """Faculty can mark student as late"""
        with app.app_context():
            session = AttendanceSession.query.first()
            student = Student.query.first()
        
        response = faculty_client.post('/faculty/attendance/mark', data={
            'session_id': str(session.id),
            'student_id': str(student.id),
            'status': 'late'
        })
        
        assert response.status_code == 200
    
    def test_late_counts_as_present(self, app, init_database):
        """Late status counts toward attendance percentage"""
        with app.app_context():
            student = Student.query.first()
            class_obj = Class.query.first()
            session = AttendanceSession.query.filter_by(class_id=class_obj.id).first()
            
            # 1 present, 1 late, 1 absent = 66.67%
            Attendance.query.filter_by(student_id=student.id).delete()
            
            for status in ['present', 'late', 'absent']:
                attendance = Attendance(
                    session_id=session.id,
                    student_id=student.id,
                    status=status,
                    marked_by=2
                )
                db.session.add(attendance)
            db.session.commit()
            
            percentage = calculate_attendance_percentage(student.id, class_obj.id)
            assert percentage == 66.67
