import mysql.connector
from mysql.connector import Error
import configparser
import os
import logging

logger = logging.getLogger(__name__)

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
                database=self.database,
                autocommit=False,
                use_pure=True,
                auth_plugin='mysql_native_password',
                ssl_verify_cert=False,
                ssl_verify_identity=False
            )
            if self.conn.is_connected():
                self.cursor = self.conn.cursor(dictionary=True)
                logger.info(f"Database connected successfully to {self.database} @ {self.host}:{self.port}")
        except Error as e:
            logger.error(f"Database connection failed: {str(e)}")
            self.conn = None
            self.cursor = None
    
    def _ensure_connection(self):
        """Ensure connection is alive, reconnect if needed."""
        try:
            if self.conn is None or not self.conn.is_connected():
                self.connect()
        except Error:
            self.connect()
    
    def execute(self, sql, params=None):
        """Returns True if executed correctly, False otherwise. Used for INSERT, UPDATE, DELETE."""
        try:
            self._ensure_connection()
            if not self.conn:
                return False
            
            self.cursor.execute(sql, params or ())
            self.conn.commit()
            return True
        except Error as e:
            logger.error(f"Execute error: {str(e)}")
            try:
                self.conn.rollback()
            except:
                pass
            return False
    
    def fetchall(self, sql, params=None):
        """Returns list of dicts. Used for SELECT queries."""
        try:
            self._ensure_connection()
            if not self.conn:
                return []
            
            self.cursor.execute(sql, params or ())
            return self.cursor.fetchall()
        except Error as e:
            logger.error(f"Fetchall error: {str(e)}")
            return []
    
    def fetchone(self, sql, params=None):
        """Returns one query result as dict. Used for SELECT queries."""
        try:
            self._ensure_connection()
            if not self.conn:
                return None
            
            self.cursor.execute(sql, params or ())
            return self.cursor.fetchone()
        except Error as e:
            logger.error(f"Fetchone error: {str(e)}")
            return None
    
    def close(self):
        """Close database connection."""
        if self.cursor:
            self.cursor.close()
        if self.conn and self.conn.is_connected():
            self.conn.close()

