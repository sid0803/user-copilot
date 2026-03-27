import sqlite3
import os

class DatabaseManager:
    def __init__(self, db_path: str = "heartbeat/db/heartbeat.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS digests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                content TEXT,
                source_type TEXT
            )
        ''')
        conn.commit()
        conn.close()

    def save_digest(self, content: str, source_type: str = "periodic"):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO digests (content, source_type) VALUES (?, ?)', (content, source_type))
        conn.commit()
        conn.close()

    def get_last_24h_digests(self) -> list:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        # Get digests from the last 24 hours
        cursor.execute("SELECT content FROM digests WHERE timestamp > datetime('now', '-1 day')")
        rows = cursor.fetchall()
        conn.close()
        return [row[0] for row in rows]
