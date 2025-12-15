"""Insert sample test data into the database using the Database helper.

This script uses the configured database in `backend/config/config.ini`.
Exits gracefully if database connection fails.
"""

import sys

from backend.database.connection import Database


def main():
    try:
        db = Database()
        db.ensure_connected_or_raise()
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        sys.exit(1)

    print("=" * 50)
    print("INSERTING TEST DATA")
    print("=" * 50)

    try:
        # Departments
        print("\n1. Adding Departments...")
        departments = [
            ('IT', 'Information Technology'),
            ('HR', 'Human Resources'),
            ('Finance', 'Finance Department'),
            ('Operations', 'Operations'),
        ]
        for dept_name, _ in departments:
            if not db.fetchone("SELECT department_id FROM Departments WHERE name = %s", (dept_name,)):
                db.execute("INSERT INTO Departments (name) VALUES (%s)", (dept_name,))
        print("   ✓ Departments added")

        # Sites
        print("\n2. Adding Sites...")
        sites = [
            ('Main Office', '123 Business Street, Downtown'),
            ('Branch A', '456 Commerce Avenue, North District'),
            ('Branch B', '789 Industrial Road, South Industrial Zone'),
            ('Head Office', '999 Executive Plaza, City Center'),
        ]
        for site_name, address in sites:
            if not db.fetchone("SELECT site_id FROM Sites WHERE site_name = %s", (site_name,)):
                db.execute("INSERT INTO Sites (site_name, address) VALUES (%s, %s)", (site_name, address))
        print("   ✓ Sites added")

        # Employees
        print("\n3. Adding Employees...")
        it_dept = db.fetchone("SELECT department_id FROM Departments WHERE name = %s", ("IT",))
        hr_dept = db.fetchone("SELECT department_id FROM Departments WHERE name = %s", ("HR",))

        if it_dept and hr_dept:
            employees = [
                ('John Doe', 500.00, it_dept['department_id']),
                ('Jane Smith', 450.00, hr_dept['department_id']),
                ('Ahmed Khan', 550.00, it_dept['department_id']),
                ('Sarah Wilson', 400.00, hr_dept['department_id']),
            ]
            for emp_name, rate, dept_id in employees:
                if not db.fetchone("SELECT employee_id FROM Employees WHERE name = %s AND department_id = %s", (emp_name, dept_id)):
                    db.execute(
                        "INSERT INTO Employees (name, hourly_rate, department_id) VALUES (%s, %s, %s)",
                        (emp_name, rate, dept_id)
                    )
            print("   ✓ Employees added")

        # Visitors
        print("\n4. Adding Visitors...")
        visitors = [
            ('Ahmed Hassan', '12345-1234567-1', '03001234567'),
            ('Fatima Ali', '23456-2345678-2', '03011234567'),
            ('Hassan Khan', '34567-3456789-3', '03021234567'),
        ]
        for full_name, cnic, contact in visitors:
            if not db.fetchone("SELECT visitor_id FROM Visitors WHERE cnic = %s", (cnic,)):
                db.execute(
                    "INSERT INTO Visitors (full_name, cnic, contact_number) VALUES (%s, %s, %s)",
                    (full_name, cnic, contact)
                )
        print("   ✓ Visitors added")

        print("\n" + "=" * 50)
        print("✓ TEST DATA INSERTED SUCCESSFULLY!")
        print("=" * 50)

    except Exception as e:
        print(f"\n✗ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
