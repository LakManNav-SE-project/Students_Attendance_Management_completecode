# Database Migration Required

## Changes Made

### Foreign Key Cascade Deletes Added
The following foreign keys now have `ondelete='CASCADE'` to prevent orphaned records:

1. **Student.user_id** → Deleting a user will delete their student profile
2. **Faculty.user_id** → Deleting a user will delete their faculty profile  
3. **Enrollment.student_id** → Deleting a student will delete their enrollments
4. **Enrollment.class_id** → Deleting a class will delete its enrollments
5. **Attendance.session_id** → Deleting a session will delete attendance records
6. **Attendance.student_id** → Deleting a student will delete their attendance
7. **Notification.user_id** → Deleting a user will delete their notifications

## Migration Steps

### Option 1: Recreate Database (Data Loss - Development Only)
```bash
# Backup existing data first!
# Delete the database file
rm instance/sams.db  # or delete via file explorer

# Run app to recreate with new schema
python app.py
```

### Option 2: Manual SQL Migration (Preserves Data)
```sql
-- For SQLite, you need to recreate tables with CASCADE
-- This is complex - use Flask-Migrate instead for production

PRAGMA foreign_keys=OFF;

-- Backup tables
CREATE TABLE students_backup AS SELECT * FROM students;
CREATE TABLE faculty_backup AS SELECT * FROM faculty;
CREATE TABLE enrollments_backup AS SELECT * FROM enrollments;
CREATE TABLE attendance_backup AS SELECT * FROM attendance;
CREATE TABLE notifications_backup AS SELECT * FROM notifications;

-- Drop old tables
DROP TABLE students;
DROP TABLE faculty;
DROP TABLE enrollments;
DROP TABLE attendance;
DROP TABLE notifications;

-- Let Flask recreate with new schema
-- Then restore data from backup tables

PRAGMA foreign_keys=ON;
```

### Option 3: Install Flask-Migrate (Recommended for Production)
```bash
pip install Flask-Migrate
```

Then add to app.py:
```python
from flask_migrate import Migrate
migrate = Migrate(app, db)
```

Run migrations:
```bash
flask db init
flask db migrate -m "Add CASCADE deletes to foreign keys"
flask db upgrade
```

## Bug Fixes Applied

1. **Section Validation**: Classes now check if students exist in the specified section before creation (shows warning if section is empty)

2. **Safe User Deletion**: 
   - Wrapped in try/except with proper error handling
   - Logs cascade deletion of all related records
   - Prevents internal server errors when deleting students

## Testing Checklist

- [ ] Delete a student user and verify no 500 error
- [ ] Verify enrollments are deleted with student
- [ ] Verify attendance records are deleted with student
- [ ] Verify notifications are deleted with user
- [ ] Try creating class with non-existent section (should show warning)
- [ ] Delete faculty user and verify classes remain but faculty profile is removed

## Notes

- CASCADE deletes are database-level constraints
- Existing database won't have these constraints until migrated
- For immediate testing, recreate the database (Option 1)
- For production, use Flask-Migrate (Option 3)
