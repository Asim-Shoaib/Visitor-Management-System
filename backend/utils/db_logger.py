from backend.database.connection import Database
from datetime import datetime
from typing import Optional

db = Database()

def log_action(user_id: int, action: str, details: Optional[str] = None):
    """
    Inserts an action log into AccessLogs table.
    """
    sql = """
        INSERT INTO AccessLogs (user_id, action, details, timestamp)
        VALUES (%s, %s, %s, %s)
    """
    timestamp = datetime.now()
    return db.execute(sql, (user_id, action, details, timestamp))

