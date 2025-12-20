import mysql.connector
from mysql.connector import Error
from mysql.connector import pooling
import configparser
import os
import logging

logger = logging.getLogger(__name__)


class Database:
    def __init__(self):
        config = configparser.ConfigParser()
        config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'config.ini')
        config.read(config_path)

        # Keep the absolute path for clearer diagnostics on failures
        self.config_path = os.path.abspath(config_path)

        self.host = config.get('database', 'host')
        self.port = config.getint('database', 'port')
        self.user = config.get('database', 'user')
        self.password = config.get('database', 'password')
        self.database = config.get('database', 'database')

        self.pool = None
        self.last_error = None
        # Create a connection pool for thread-safe, concurrent usage
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
            }

            if self.host in ('localhost', '127.0.0.1', '::1'):
                connect_params['ssl_disabled'] = True
            else:
                connect_params['ssl_verify_cert'] = False
                connect_params['ssl_verify_identity'] = False

            # Use a connection pool rather than a single shared connection to avoid
            # concurrent access issues and random disconnects under load.
            pool_name = 'vms_pool'
            pool_size = 5
            self.pool = pooling.MySQLConnectionPool(pool_name=pool_name, pool_size=pool_size, **connect_params)
            # Test a connection from the pool
            conn = self.pool.get_connection()
            if conn.is_connected():
                conn.close()
                logger.info(f"Database pool created successfully to {self.database} @ {self.host}:{self.port} (pool_size={pool_size})")
        except Error as e:
            logger.exception(
                f"Database connection failed for {self.user}@{self.host}:{self.port}/{self.database} "
                f"(config={self.config_path}): {str(e)}"
            )
            self.last_error = e
            self.pool = None
        except Exception as e:
            logger.exception(
                f"Database connection error for {self.user}@{self.host}:{self.port}/{self.database} "
                f"(config={self.config_path}): {str(e)}"
            )
            self.last_error = e
            self.pool = None

    def _get_conn_cursor(self):
        """Get a connection and cursor from the pool. Caller must close the cursor and connection."""
        if not self.pool:
            self.connect()
            if not self.pool:
                raise Exception("Database pool not available")

        conn = self.pool.get_connection()
        cursor = conn.cursor(dictionary=True)
        return conn, cursor

    def ensure_connected_or_raise(self):
        """Ensure we have a working connection from the pool or raise an informative error."""
        # Ensure the pool exists
        self._ensure_connection()
        if not self.pool:
            err = self.last_error if self.last_error is not None else Exception("Unable to connect to database")
            raise Exception(f"Database connection unavailable: {err}")

        # Borrow a connection and validate it
        try:
            conn = self.pool.get_connection()
            ok = conn.is_connected()
            conn.close()
        except Exception as e:
            self.last_error = e
            raise Exception(f"Database connection test failed: {e}")

        if not ok:
            err = self.last_error if self.last_error is not None else Exception("Unable to connect to database")
            raise Exception(f"Database connection unavailable: {err}")

    def _ensure_connection(self):
        # For pool-based connections, ensure pool exists
        try:
            if self.pool is None:
                self.connect()
        except Exception:
            try:
                self.connect()
            except Exception:
                pass

    def execute(self, sql, params=None):
        conn = None
        cursor = None
        import time
        try:
            self._ensure_connection()
            conn, cursor = self._get_conn_cursor()
            start = time.time()
            cursor.execute(sql, params or ())
            duration = time.time() - start
            if duration > 0.25:
                logger.warning(f"Slow query detected ({duration:.3f}s): {sql}")
            conn.commit()
            return True
        except Exception as e:
            logger.exception(f"Execute error: {str(e)}")
            try:
                if conn:
                    conn.rollback()
            except Exception:
                logger.exception("Failed to rollback transaction")
            return False
        finally:
            try:
                if cursor:
                    cursor.close()
                if conn:
                    conn.close()
            except Exception:
                logger.exception("Failed to close DB resources in execute")

    def fetchall(self, sql, params=None):
        conn = None
        cursor = None
        try:
            self._ensure_connection()
            conn, cursor = self._get_conn_cursor()
            import time
            start = time.time()
            cursor.execute(sql, params or ())
            rows = cursor.fetchall()
            duration = time.time() - start
            if duration > 0.25:
                logger.warning(f"Slow query detected ({duration:.3f}s): {sql}")
            return rows if rows else []
        except Exception as e:
            logger.exception(f"Fetchall error: {str(e)}")
            return []
        finally:
            try:
                if cursor:
                    cursor.close()
                if conn:
                    conn.close()
            except Exception:
                logger.exception("Failed to close DB resources in fetchall")

    def fetchone(self, sql, params=None):
        conn = None
        cursor = None
        try:
            self._ensure_connection()
            conn, cursor = self._get_conn_cursor()
            import time
            start = time.time()
            cursor.execute(sql, params or ())
            row = cursor.fetchone()
            duration = time.time() - start
            if duration > 0.25:
                logger.warning(f"Slow query detected ({duration:.3f}s): {sql}")
            return row if row else None
        except Exception as e:
            logger.exception(f"Fetchone error: {str(e)}")
            return None
        finally:
            try:
                if cursor:
                    cursor.close()
                if conn:
                    conn.close()
            except Exception:
                logger.exception("Failed to close DB resources in fetchone")

    def close(self):
        # Close pool (no direct close API; clear reference)
        self.pool = None

