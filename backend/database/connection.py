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
            connect_params = {
                'host': self.host,
                'port': self.port,
                'user': self.user,
                'password': self.password,
                'database': self.database,
                'autocommit': False,
                'use_pure': True,
                'charset': 'utf8mb4',
                'auth_plugin': 'mysql_native_password',
            }

            if self.host in ('localhost', '127.0.0.1', '::1'):
                connect_params['ssl_disabled'] = True
            else:
                connect_params['ssl_verify_cert'] = False
                connect_params['ssl_verify_identity'] = False

            self.conn = mysql.connector.connect(**connect_params)
            if self.conn.is_connected():
                self.cursor = self.conn.cursor(dictionary=True, buffered=True)
                logger.info(f"Database connected successfully to {self.database} @ {self.host}:{self.port}")
        except Error as e:
            logger.error(f"Database connection failed: {str(e)}")
            self.conn = None
            self.cursor = None
        except Exception as e:
            logger.error(f"Database connection error: {str(e)}")
            self.conn = None
            self.cursor = None

    def _ensure_connection(self):
        try:
            if self.conn is None or not self.conn.is_connected():
                self.connect()
        except Exception:
            try:
                self.connect()
            except Exception:
                pass

    def execute(self, sql, params=None):
        try:
            self._ensure_connection()
            if not self.conn or not self.cursor:
                return False

            self.cursor.execute(sql, params or ())
            self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"Execute error: {str(e)}")
            try:
                if self.conn:
                    self.conn.rollback()
            except Exception:
                pass
            return False

    def fetchall(self, sql, params=None):
        try:
            self._ensure_connection()
            if not self.conn or not self.cursor:
                return []

            self.cursor.execute(sql, params or ())
            rows = self.cursor.fetchall()
            return rows if rows else []
        except Exception as e:
            logger.error(f"Fetchall error: {str(e)}")
            return []

    def fetchone(self, sql, params=None):
        try:
            self._ensure_connection()
            if not self.conn or not self.cursor:
                return None

            self.cursor.execute(sql, params or ())
            row = self.cursor.fetchone()
            return row if row else None
        except Exception as e:
            logger.error(f"Fetchone error: {str(e)}")
            return None

    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.conn and self.conn.is_connected():
            self.conn.close()

