"""Initialize database with test data for testing"""
from app import app, db, User, Student, Faculty, Course, Class, Enrollment, AttendanceSession, Attendance
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta, time, date

def initialize_test_data():
    """Create test data for all user roles and features"""
    with app.app_context():
        # Clear existing data
        db.drop_all()
        db.create_all()
        
        print("Creating users...")
        # Admin
        admin_user = User(
            username='admin',
            password_hash=generate_password_hash('admin123'),
            role='admin',
            email='admin@test.com',
            full_name='Administrator'
        )
        db.session.add(admin_user)
        
        # Faculty users (3)
        faculty_users = []
        for i in range(1, 4):
            user = User(
                username=f'faculty{i}',
                password_hash=generate_password_hash('faculty123'),
                role='faculty',
                email=f'faculty{i}@test.com',
                full_name=f'Faculty Member {i}'
            )
            faculty_users.append(user)
            db.session.add(user)
        
        # Student users (10)
        student_users = []
        for i in range(1, 11):
            user = User(
                username=f'student{i}',
                password_hash=generate_password_hash('student123'),
                role='student',
                email=f'student{i}@test.com',
                full_name=f'Student {i}'
            )
            student_users.append(user)
            db.session.add(user)
        
        db.session.commit()
        print(f"Created {len(faculty_users)} faculty and {len(student_users)} student users")
        
        # Create faculty profiles
        print("Creating faculty profiles...")
        faculties = []
        for i, user in enumerate(faculty_users, 1):
            faculty = Faculty(
                user_id=user.id,
                faculty_id=f'FAC{i:03d}',
                department='Computer Science',
                designation='Assistant Professor'
            )
            faculties.append(faculty)
            db.session.add(faculty)
        
        # Create student profiles
        print("Creating student profiles...")
        students = []
        for i, user in enumerate(student_users, 1):
            student = Student(
                user_id=user.id,
                student_id=f'STU{i:03d}',
                department='Computer Science',
                year=2,
                section='A',
                parent_email=f'parent{i}@test.com',
                parent_phone=f'99876{i:05d}'
            )
            students.append(student)
            db.session.add(student)
        
        db.session.commit()
        
        # Create courses
        print("Creating courses...")
        courses = []
        course_data = [
            ('CS101', 'Data Structures'),
            ('CS102', 'Algorithms'),
            ('CS103', 'Database Systems')
        ]
        for code, name in course_data:
            course = Course(
                course_code=code,
                course_name=name,
                credits=4
            )
            courses.append(course)
            db.session.add(course)
        
        db.session.commit()
        
        # Create classes
        print("Creating classes...")
        classes = []
        for i, (course, faculty) in enumerate(zip(courses, faculties), 1):
            class_obj = Class(
                course_id=course.id,
                faculty_id=faculty.id,
                section='A',
                room=f'R{i}01'
            )
            classes.append(class_obj)
            db.session.add(class_obj)
        
        db.session.commit()
        
        # Enroll all students in all classes
        print("Creating enrollments...")
        for student in students:
            for class_obj in classes:
                enrollment = Enrollment(
                    student_id=student.id,
                    class_id=class_obj.id
                )
                db.session.add(enrollment)
        
        db.session.commit()
        
        # Create attendance sessions (last 10 days)
        print("Creating attendance sessions...")
        sessions_created = 0
        for day_offset in range(10):
            session_date = date.today() - timedelta(days=day_offset)
            
            for class_obj in classes:
                # Create 1 session per class per day
                session = AttendanceSession(
                    class_id=class_obj.id,
                    date=session_date,
                    start_time=time(9, 0),
                    end_time=time(10, 0),
                    created_by=class_obj.faculty_id
                )
                db.session.add(session)
                sessions_created += 1
        
        db.session.commit()
        print(f"Created {sessions_created} attendance sessions")
        
        # Mark attendance for all sessions
        print("Marking attendance...")
        all_sessions = AttendanceSession.query.all()
        attendance_records = 0
        
        for session in all_sessions:
            class_obj = Class.query.get(session.class_id)
            enrollments = Enrollment.query.filter_by(class_id=class_obj.id).all()
            
            for enrollment in enrollments:
                # 80% present, 20% absent
                status = 'present' if (enrollment.student_id + session.id) % 5 != 0 else 'absent'
                
                attendance = Attendance(
                    session_id=session.id,
                    student_id=enrollment.student_id,
                    status=status,
                    marked_by=class_obj.faculty_id
                )
                db.session.add(attendance)
                attendance_records += 1
        
        db.session.commit()
        print(f"Created {attendance_records} attendance records")
        
        print("\n=== Database Initialization Complete ===")
        print(f"Users: {User.query.count()}")
        print(f"Students: {Student.query.count()}")
        print(f"Faculty: {Faculty.query.count()}")
        print(f"Courses: {Course.query.count()}")
        print(f"Classes: {Class.query.count()}")
        print(f"Enrollments: {Enrollment.query.count()}")
        print(f"Sessions: {AttendanceSession.query.count()}")
        print(f"Attendance: {Attendance.query.count()}")
        
        print("\n=== Login Credentials ===")
        print("Admin: username=admin, password=admin123")
        print("Faculty: username=faculty1-3, password=faculty123")
        print("Student: username=student1-10, password=student123")

if __name__ == '__main__':
    initialize_test_data()
