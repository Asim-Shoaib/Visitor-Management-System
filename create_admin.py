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
    
    # Create roles if they don't exist
    cursor.execute("INSERT IGNORE INTO Roles (role_name, description) VALUES ('admin', 'Administrator')")
    cursor.execute("INSERT IGNORE INTO Roles (role_name, description) VALUES ('security', 'Security Personnel')")
    
    # Create admin user
    admin_password = sha256('admin123'.encode()).hexdigest()
    cursor.execute(
        "INSERT INTO Users (username, password_hash, role_id) VALUES (%s, %s, (SELECT role_id FROM Roles WHERE role_name = 'admin'))",
        ('admin', admin_password)
    )
    
    conn.commit()
    print("✓ Admin user created successfully!")
    print("  Username: admin")
    print("  Password: admin123")
    
except Exception as e:
    print(f"✗ Error: {str(e)}")
finally:
    if conn:
        conn.close()
