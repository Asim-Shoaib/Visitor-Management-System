import mysql.connector
from hashlib import sha256

# Database config
config = {
    'host': 'localhost',
    'user': 'root',
    'password': '280184',
    'database': 'Visitor_Management_System'
}

try:
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()
    
    print("=" * 50)
    print("INSERTING TEST DATA")
    print("=" * 50)
    
    # Insert departments
    print("\n1. Adding Departments...")
    departments = [
        ('IT', 'Information Technology'),
        ('HR', 'Human Resources'),
        ('Finance', 'Finance Department'),
        ('Operations', 'Operations'),
    ]
    for dept_name, description in departments:
        cursor.execute(
            "INSERT IGNORE INTO Departments (name) VALUES (%s)",
            (dept_name,)
        )
    print("   ✓ Departments added")
    
    # Insert sites
    print("\n2. Adding Sites...")
    sites = [
        ('Main Office', '123 Business Street, Downtown'),
        ('Branch A', '456 Commerce Avenue, North District'),
        ('Branch B', '789 Industrial Road, South Industrial Zone'),
        ('Head Office', '999 Executive Plaza, City Center'),
    ]
    for site_name, address in sites:
        cursor.execute(
            "INSERT IGNORE INTO Sites (site_name, address) VALUES (%s, %s)",
            (site_name, address)
        )
    print("   ✓ Sites added")
    
    # Insert employees
    print("\n3. Adding Employees...")
    cursor.execute("SELECT department_id FROM Departments WHERE name = 'IT' LIMIT 1")
    it_dept = cursor.fetchone()
    cursor.execute("SELECT department_id FROM Departments WHERE name = 'HR' LIMIT 1")
    hr_dept = cursor.fetchone()
    
    if it_dept and hr_dept:
        employees = [
            ('John Doe', 500.00, it_dept[0]),
            ('Jane Smith', 450.00, hr_dept[0]),
            ('Ahmed Khan', 550.00, it_dept[0]),
            ('Sarah Wilson', 400.00, hr_dept[0]),
        ]
        for emp_name, rate, dept_id in employees:
            cursor.execute(
                "INSERT IGNORE INTO Employees (name, hourly_rate, department_id) VALUES (%s, %s, %s)",
                (emp_name, rate, dept_id)
            )
        print("   ✓ Employees added")
    
    # Insert visitors
    print("\n4. Adding Visitors...")
    visitors = [
        ('Ahmed Hassan', '12345-1234567-1', '03001234567'),
        ('Fatima Ali', '23456-2345678-2', '03011234567'),
        ('Hassan Khan', '34567-3456789-3', '03021234567'),
    ]
    for full_name, cnic, contact in visitors:
        cursor.execute(
            "INSERT IGNORE INTO Visitors (full_name, cnic, contact_number) VALUES (%s, %s, %s)",
            (full_name, cnic, contact)
        )
    print("   ✓ Visitors added")
    
    conn.commit()
    print("\n" + "=" * 50)
    print("✓ TEST DATA INSERTED SUCCESSFULLY!")
    print("=" * 50)
    print("\nYou can now:")
    print("  • Login as admin / admin123")
    print("  • Go to Visitor Entry and select from Sites dropdown")
    print("  • Add more employees via Employee Management")
    print("  • Generate QR codes for employees")
    print("=" * 50)
    
except Exception as e:
    print(f"\n✗ Error: {str(e)}")
finally:
    if conn:
        conn.close()
