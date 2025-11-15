#!/bin/bash

# SAMS - Student Attendance Management System
# Quick Start Script

echo "======================================"
echo "SAMS - Student Attendance Management"
echo "======================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "✓ Python 3 found"

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install --break-system-packages -q Flask Flask-SQLAlchemy qrcode[pil] reportlab python-docx

if [ $? -eq 0 ]; then
    echo "✓ Dependencies installed successfully"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi

# Run the application
echo ""
echo "Starting SAMS application..."
echo ""
echo "======================================"
echo "Access the application at:"
echo "http://localhost:5000"
echo "======================================"
echo ""
echo "Default Login Credentials:"
echo "-----------------------------------"
echo "Admin    : admin / admin123"
echo "Faculty  : faculty1 / faculty123"
echo "Student  : student1 / student123"
echo "======================================"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python3 app.py