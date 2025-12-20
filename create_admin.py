"""Create an admin user if it doesn't already exist.

Uses backend.database.connection.Database to read credentials from
`backend/config/config.ini`. Exits gracefully on connection failure.
"""

from hashlib import sha256
import sys

from backend.database.connection import Database


def main():
    try:
        db = Database()
        db.ensure_connected_or_raise()
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        sys.exit(1)

    try:
        # Ensure roles exist
        role_admin = db.fetchone("SELECT role_id FROM Roles WHERE role_name = %s", ("admin",))
        if not role_admin:
            if not db.execute("INSERT INTO Roles (role_name, description) VALUES (%s, %s)", ("admin", "Administrator")):
                print("✗ Failed to create admin role")
                sys.exit(1)

        role_security = db.fetchone("SELECT role_id FROM Roles WHERE role_name = %s", ("security",))
        if not role_security:
            db.execute("INSERT INTO Roles (role_name, description) VALUES (%s, %s)", ("security", "Security Personnel"))

        # Check if admin user exists
        existing = db.fetchone("SELECT user_id FROM Users WHERE username = %s", ("admin",))
        if existing:
            print("✓ Admin user already exists. No changes made.")
            return

        # Insert admin user
        admin_password = sha256("admin123".encode()).hexdigest()
        success = db.execute(
            "INSERT INTO Users (username, password_hash, role_id) VALUES (%s, %s, (SELECT role_id FROM Roles WHERE role_name = 'admin'))",
            ("admin", admin_password),
        )

        if success:
            print("Admin user created successfully.")
            print("Username: admin")
            print("Default password set. Change it after first login.")
        else:
            print("Failed to create admin user")
            sys.exit(1)

    except Exception as e:
        print(f"✗ Error while creating admin: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
