# SAMS - Student Attendance Management System

A comprehensive Flask-based web application for managing student attendance with role-based access control, QR code scanning, and detailed reporting.

## Features

### Admin Features
- ✅ User Management (Create, View, Delete users)
- ✅ Course Management
- ✅ Class Management
- ✅ Comprehensive Attendance Reports
- ✅ System Audit Logs
- ✅ Dashboard with Statistics

### Faculty Features
- ✅ Create Attendance Sessions
- ✅ Generate QR Codes for attendance
- ✅ Manual Attendance Marking
- ✅ View Class Details and Student Lists
- ✅ Export Reports (CSV, PDF)
- ✅ Class-wise Attendance Analytics

### Student Features
- ✅ View Attendance Summary
- ✅ Scan QR Codes to mark attendance
- ✅ Detailed Attendance History
- ✅ Notifications for low attendance
- ✅ Course-wise Attendance Breakdown

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Setup Steps

1. **Install Dependencies**
```bash
pip install -r requirements.txt
```

2. **Run the Application**
```bash
python app.py
```

3. **Access the Application**
Open your browser and navigate to: `http://localhost:5000`

## Default Login Credentials

After first run, the database will be initialized with sample data:

- **Admin Account**
  - Username: `admin`
  - Password: `admin123`

- **Faculty Account**
  - Username: `faculty1`
  - Password: `faculty123`

- **Student Account**
  - Username: `student1`
  - Password: `student123`

## Project Structure

```
sams/
├── app.py                          # Main Flask application
├── requirements.txt                # Python dependencies
├── sams.db                         # SQLite database (created on first run)
├── templates/                      # HTML templates
│   ├── base.html                   # Base template
│   ├── login.html                  # Login page
│   ├── admin/                      # Admin templates
│   │   ├── dashboard.html
│   │   ├── users.html
│   │   ├── add_user.html
│   │   ├── courses.html
│   │   ├── add_course.html
│   │   ├── classes.html
│   │   ├── add_class.html
│   │   ├── reports.html
│   │   └── attendance_report.html
│   ├── faculty/                    # Faculty templates
│   │   ├── dashboard.html
│   │   ├── classes.html
│   │   ├── class_detail.html
│   │   ├── create_session.html
│   │   ├── session_detail.html
│   │   ├── reports.html
│   │   └── class_report.html
│   └── student/                    # Student templates
│       ├── dashboard.html
│       ├── attendance.html
│       ├── class_attendance.html
│       ├── scan_qr.html
│       └── notifications.html
└── static/                         # Static files
    └── css/
        └── style.css               # Custom CSS

```

## Key Features Explained

### 1. Role-Based Access Control (RBAC)
- Three distinct roles: Admin, Faculty, and Student
- Each role has specific permissions and access levels
- Secure session management with 30-minute timeout

### 2. Attendance Management
- Multiple methods: Manual marking, QR code scanning
- Real-time attendance tracking
- Automated absence notifications

### 3. QR Code System
- Faculty can generate time-limited QR codes
- Students scan QR codes to mark attendance
- QR codes expire after 1 hour for security

### 4. Reporting & Analytics
- Comprehensive attendance reports
- Export to CSV and PDF formats
- Class-wise and student-wise analytics
- Attendance percentage calculations

### 5. Notification System
- Low attendance warnings (< 75%)
- Email notifications to parents
- In-app notifications for students

### 6. Audit Logging
- All user actions are logged
- IP address tracking
- Timestamp for every action

## Database Schema

The application uses SQLite with the following main tables:

- **users**: User accounts with role-based access
- **students**: Student profiles and information
- **faculty**: Faculty profiles and information
- **courses**: Course catalog
- **classes**: Class schedules and assignments
- **enrollments**: Student-class enrollments
- **attendance_sessions**: Attendance session metadata
- **attendance**: Individual attendance records
- **notifications**: User notifications
- **audit_logs**: System audit trail

## Email Configuration

To enable email notifications, configure SMTP settings in `app.py`:

```python
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USERNAME = "your_email@gmail.com"
SMTP_PASSWORD = "your_app_password"
```

Then uncomment the email sending code in the `send_email()` function.

## Security Features

- ✅ Password hashing using Werkzeug's security functions
- ✅ Session management with CSRF protection
- ✅ Role-based access control decorators
- ✅ SQL injection prevention via SQLAlchemy ORM
- ✅ XSS protection through template escaping
- ✅ Audit logging for compliance

## Customization

### Adding New Roles
1. Update the `role` field in the User model
2. Create new decorators in `app.py`
3. Add corresponding routes and templates

### Extending Features
- Add biometric attendance support
- Integrate with external SMS gateways
- Add more report types
- Implement batch operations

## Continuous Integration

Automated testing runs in GitHub Actions via `.github/workflows/ci.yml` whenever you push to `main` or open a pull request targeting `main`.

- **Environment:** Ubuntu runner with Python 3.12
- **Dependencies:** Cached `pip` install from `requirements.txt`
- **Validation:** Executes the entire pytest suite (`python -m pytest tests/ -v --maxfail=1 --disable-warnings`)
- **Artifacts:** On failure, uploads `.pytest_cache` to help with debugging

To verify locally before pushing, run:

```bash
python -m pytest tests/ -v --maxfail=1 --disable-warnings
```

## Troubleshooting

### Common Issues

**Database not found**
```bash
# Delete existing database and restart
rm sams.db
python app.py
```

**Port already in use**
```python
# Change port in app.py
app.run(debug=True, host='0.0.0.0', port=5001)
```

**Template not found errors**
- Ensure all template files are in the correct directory
- Check file permissions

## Performance Optimization

For production deployment:
1. Set `debug=False` in `app.run()`
2. Use a production WSGI server (Gunicorn, uWSGI)
3. Consider PostgreSQL instead of SQLite
4. Enable caching for static files
5. Add database indexing

## Contributing

This is an educational project based on the Software Requirements Specification and Software Architecture Document for the Student Attendance Management System.

## License

Educational use only. Part of academic coursework.

## Authors

- Lakshya Sukruthi N
- N V Manya
- Navyashree J

## Version History

- v1.0 (2025) - Initial release with full CRUD operations, reporting, and QR code attendance