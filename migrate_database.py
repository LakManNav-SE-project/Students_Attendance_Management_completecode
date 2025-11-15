"""
Database Migration Script
Adds CASCADE delete constraints to foreign keys while preserving all data
"""

import sqlite3
import os
from datetime import datetime

def migrate_database():
    db_path = 'instance/sams.db'
    backup_path = f'instance/sams_migration_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db'
    
    print(f"Starting migration for {db_path}")
    print(f"Creating backup at {backup_path}")
    
    # Create another backup
    if os.path.exists(db_path):
        import shutil
        shutil.copy2(db_path, backup_path)
        print("✓ Backup created")
    else:
        print("✗ Database not found!")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Enable foreign keys (important!)
    cursor.execute("PRAGMA foreign_keys = OFF;")
    
    try:
        print("\n1. Creating temporary tables with existing data...")
        
        # Backup all affected tables
        tables_to_backup = [
            'students', 'faculty', 'enrollments', 
            'attendance', 'notifications'
        ]
        
        for table in tables_to_backup:
            cursor.execute(f"CREATE TABLE {table}_temp AS SELECT * FROM {table};")
            count = cursor.execute(f"SELECT COUNT(*) FROM {table}_temp").fetchone()[0]
            print(f"   ✓ Backed up {count} rows from {table}")
        
        print("\n2. Dropping old tables...")
        for table in tables_to_backup:
            cursor.execute(f"DROP TABLE {table};")
            print(f"   ✓ Dropped {table}")
        
        print("\n3. Creating new tables with CASCADE constraints...")
        
        # Recreate students table
        cursor.execute("""
            CREATE TABLE students (
                id INTEGER PRIMARY KEY,
                user_id INTEGER NOT NULL,
                student_id VARCHAR(20) UNIQUE NOT NULL,
                department VARCHAR(100),
                year INTEGER,
                section VARCHAR(10),
                parent_email VARCHAR(120),
                parent_phone VARCHAR(20),
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );
        """)
        print("   ✓ Created students table")
        
        # Recreate faculty table
        cursor.execute("""
            CREATE TABLE faculty (
                id INTEGER PRIMARY KEY,
                user_id INTEGER NOT NULL,
                faculty_id VARCHAR(20) UNIQUE NOT NULL,
                department VARCHAR(100),
                designation VARCHAR(50),
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );
        """)
        print("   ✓ Created faculty table")
        
        # Recreate enrollments table
        cursor.execute("""
            CREATE TABLE enrollments (
                id INTEGER PRIMARY KEY,
                student_id INTEGER NOT NULL,
                class_id INTEGER NOT NULL,
                enrollment_date DATETIME,
                FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
                FOREIGN KEY (class_id) REFERENCES classes(id) ON DELETE CASCADE
            );
        """)
        print("   ✓ Created enrollments table")
        
        # Recreate attendance table
        cursor.execute("""
            CREATE TABLE attendance (
                id INTEGER PRIMARY KEY,
                session_id INTEGER NOT NULL,
                student_id INTEGER NOT NULL,
                status VARCHAR(20) NOT NULL,
                marked_at DATETIME,
                marked_by INTEGER,
                method VARCHAR(20),
                FOREIGN KEY (session_id) REFERENCES attendance_sessions(id) ON DELETE CASCADE,
                FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
                FOREIGN KEY (marked_by) REFERENCES users(id)
            );
        """)
        print("   ✓ Created attendance table")
        
        # Recreate notifications table
        cursor.execute("""
            CREATE TABLE notifications (
                id INTEGER PRIMARY KEY,
                user_id INTEGER NOT NULL,
                title VARCHAR(100) NOT NULL,
                message TEXT NOT NULL,
                type VARCHAR(20),
                is_read BOOLEAN,
                created_at DATETIME,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );
        """)
        print("   ✓ Created notifications table")
        
        print("\n4. Restoring data from backups...")
        
        # Restore data
        for table in tables_to_backup:
            cursor.execute(f"INSERT INTO {table} SELECT * FROM {table}_temp;")
            count = cursor.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            print(f"   ✓ Restored {count} rows to {table}")
        
        print("\n5. Cleaning up temporary tables...")
        for table in tables_to_backup:
            cursor.execute(f"DROP TABLE {table}_temp;")
            print(f"   ✓ Dropped {table}_temp")
        
        # Re-enable foreign keys
        cursor.execute("PRAGMA foreign_keys = ON;")
        
        conn.commit()
        print("\n✅ Migration completed successfully!")
        print(f"✅ Backup saved at: {backup_path}")
        print("\n⚠️  If anything goes wrong, you can restore from backup:")
        print(f"   Copy-Item '{backup_path}' 'instance\\sams.db' -Force")
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        print("Rolling back changes...")
        conn.rollback()
        print("\n⚠️  Database unchanged. Backup is safe.")
        raise
    
    finally:
        conn.close()

if __name__ == '__main__':
    print("="*60)
    print("DATABASE MIGRATION: Adding CASCADE Delete Constraints")
    print("="*60)
    
    response = input("\n⚠️  This will modify your database. A backup will be created.\nContinue? (yes/no): ")
    
    if response.lower() in ['yes', 'y']:
        migrate_database()
    else:
        print("Migration cancelled.")
