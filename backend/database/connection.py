import mysql.connector
from mysql.connector import Error
import configparser
import os

class Database:
    def __init__(self):
        config = configparser.ConfigParser()
        config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'config.ini')
        config.read(config_path)
        
        self.host = config.get('database', 'host')
        self.port = config.getint('database', 'port')
        self.user = config.get('database', 'user')
        self.password = config.get('database', 'password')
        self.database = config.get('database', 'database')
        
        self.conn = None
        self.cursor = None
        self.connect()
    
    def connect(self):
        try:
            self.conn = mysql.connector.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database
            )
            if self.conn.is_connected():
                print("Connected to MySQL successfully.")
                self.cursor = self.conn.cursor(dictionary=True)
        except Error as e:
            print(f"Error connecting to MySQL: {e}")
            self.conn = None
            self.cursor = None
    
    def execute(self, sql, params=None):
        """Returns True if executed correctly, False otherwise. Used for INSERT, UPDATE, DELETE."""
        if not self.conn or not self.conn.is_connected():
            self.connect()
            if not self.conn:
                print("No database connection")
                return False
        
        try:
            self.cursor.execute(sql, params or ())
            self.conn.commit()
            return True
        except Error as e:
            print(f"Error executing query: {e}")
            self.conn.rollback()
            return False
    
    def fetchall(self, sql, params=None):
        """Returns list of dicts. Used for SELECT queries."""
        if not self.conn or not self.conn.is_connected():
            self.connect()
            if not self.conn:
                print("No database connection")
                return []
        
        try:
            self.cursor.execute(sql, params or ())
            return self.cursor.fetchall()
        except Error as e:
            print(f"Error fetching data: {e}")
            return []
    
    def fetchone(self, sql, params=None):
        """Returns one query result as dict. Used for SELECT queries."""
        if not self.conn or not self.conn.is_connected():
            self.connect()
            if not self.conn:
                print("No database connection")
                return None
        
        try:
            self.cursor.execute(sql, params or ())
            return self.cursor.fetchone()
        except Error as e:
            print(f"Error fetching data: {e}")
            return None
    
    def close(self):
        """Close database connection."""
        if self.cursor:
            self.cursor.close()
        if self.conn and self.conn.is_connected():
            self.conn.close()
            print("MySQL connection closed.")

