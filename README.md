# SAMS - Student Attendance Management System

A comprehensive Flask-based web application for managing student attendance with role-based access control,  and detailed reporting.

## Features

### Admin Features
-  User Management (Create, View, Delete users)
-  Course Management
-  Class Management
-  Comprehensive Attendance Reports
-  System Audit Logs
-  Dashboard with Statistics

### Faculty Features
-  Create Attendance Sessions
-  Manual Attendance Marking
-  View Class Details and Student Lists
-  Export Reports (CSV, PDF)
-  Class-wise Attendance Analytics

### Student Features
-  View Attendance Summary
-  Detailed Attendance History
-  Course-wise Attendance Breakdown

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
- Manual marking
- Real-time attendance tracking

### 3. Reporting & Analytics
- Comprehensive attendance reports
- Export to CSV and PDF formats
- Class-wise and student-wise analytics
- Attendance percentage calculations


### 4. Audit Logging
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
- **audit_logs**: System audit trail


## Security Features

-  Password hashing using Werkzeug's security functions
-  Session management with CSRF protection
-  Role-based access control decorators
-  SQL injection prevention via SQLAlchemy ORM
-  XSS protection through template escaping
-  Audit logging for compliance

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
- **Validation:** Executes the pytest suite with coverage enabled (`python -m pytest tests/ -v --maxfail=1 --disable-warnings --cov=. --cov-branch`)
- **Artifacts:** Always uploads the generated `coverage.xml` and `htmlcov/` HTML report plus `.pytest_cache` on failure for easy inspection

To verify locally before pushing (and produce the same coverage reports), run:

```bash
python -m pytest tests/ -v --maxfail=1 --disable-warnings \
  --cov=. --cov-branch \
  --cov-report=term-missing \
  --cov-report=xml \
  --cov-report=html
```

The above command writes an interactive HTML report to `htmlcov/index.html` and a machine-readable `coverage.xml` file that can be consumed by quality gates or IDE plugins.

## Containerized Deployment

The repository ships with a ready-to-run `Dockerfile` so you can package the full Flask stack behind Gunicorn.

```bash
# Build the image locally
docker build -t sams:latest .

# Run it on port 5000
docker run --rm -p 5000:5000 sams:latest
```

Environment variables:
- `PORT` (default `5000`): change if your platform injects a custom port (e.g., Render/Heroku).

## Continuous Delivery

Workflow `.github/workflows/cd.yml` promotes every `main` push by:
1. Re-running the pytest suite for safety.
2. Building the Docker image defined above.
3. Publishing the image to GitHub Container Registry (GHCR) as `ghcr.io/<owner>/students_attendance_management` with both `latest` and commit-sha tags.

The job authenticates using the built-in `GITHUB_TOKEN`, so no manual secrets are required. You can pull the latest artifact onto any deployment target with:

```bash
docker pull ghcr.io/<owner>/students_attendance_management:latest
```

Replace `<owner>` with your GitHub org/user (`lakmannav-se-project`).

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

- v1.0 (2025) - Initial release with full CRUD operations and reporting
