"""
This module contains local database initialization for Aurelius app
"""
import sqlite3


class AureliusDB:
    """
    This class contains database initialization methods 
    """

    def __init__(self, db_path="app/db/aurelius.db"):
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self._create_tables()

    def _create_tables(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_info (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          name TEXT UNIQUE NOT NULL,
          current_model TEXT NOT NULL       
        )

        """)

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS recent_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_memory_context (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key TEXT UNIQUE,
            value TEXT,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS conversation_context (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            summary TEXT,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)

        self.conn.commit()

    def register_user(self, name, model):
        """
        This method creates de aurelius user on the local database
        """
        self.cursor.execute("""
        INSERT INTO user_info (id, name, current_model)
        VALUES (?, ?, ?)
    """, (1, name, model))
        self.conn.commit()

    def is_user_registerd(self):
        """
        This method returns the user name 
        to verify if is already registered
        """
        self.cursor.execute("""
        SELECT name FROM user_info WHERE id = ?
    """, (1,))

        return self.cursor.fetchone()

    def get_user_data(self):
        """
        This method retrieves all the user stored data
        """
        self.cursor.execute("""
        SELECT name, current_model FROM user_info WHERE id = ?
    """, (1,))

        return self.cursor.fetchone()

    def update_user_data(self, name, model):
        """
        This method updates de user name and ollama model to be used
        """
        self.cursor.execute("""
        UPDATE user_info
            SET name = ?,
            current_model =? 
        WHERE id = ?
    """, (name, model, 1))
        self.conn.commit()

    def add_message(self, content):
        """
        This method adds a recent message to the datebase
        """
        self.cursor.execute("""
        INSERT INTO recent_messages (content)
        VALUES (?)
        """, (content,))
        self.conn.commit()

    def get_recent_messages(self, limit=5):
        """
        This method gets the 10 recent message from the user
        """
        self.cursor.execute("""
        SELECT content FROM recent_messages
        ORDER BY id DESC
        LIMIT ?
        """, (limit,))
        return self.cursor.fetchall()[::-1]

    def clear_old_messages(self, keep=10):
        """
        This method clears all the old messages between the llm and the user
        """
        self.cursor.execute("""
        DELETE FROM recent_messages
        WHERE id NOT IN (
            SELECT id FROM recent_messages ORDER BY id DESC LIMIT ?
        )
        """, (keep,))
        self.conn.commit()

    def save_memory(self, key, value):
        """
        This method saves an important value for understand better the user
        context
        """
        self.cursor.execute("""
        INSERT INTO user_memory_context (key, value)
        VALUES (?, ?)
        ON CONFLICT(key) DO UPDATE SET value=excluded.value, updated_at=CURRENT_TIMESTAMP
        """, (key, value))
        self.conn.commit()

    def load_memory(self):
        """
        This method loads all the memories saved from the user to improve context
        """
        self.cursor.execute("SELECT key, value FROM user_memory_context")
        return dict(self.cursor.fetchall())

    def save_summary(self, summary):
        """
        This method saves a summary of recent conversations 
        to improve futire conversations context
        """
        self.cursor.execute("""
        INSERT INTO conversation_context (summary)
        VALUES (?)
        """, (summary,))
        self.conn.commit()

    def get_summary(self):
        """
        This method gets the summary of the last conversation to improve context
        """
        self.cursor.execute("""
        SELECT summary FROM conversation_context
        ORDER BY id DESC LIMIT 1
        """)
        row = self.cursor.fetchone()
        return row[0] if row else ""

    def get_user_model(self):
        """
        This method returns de user ollama model to be used
        """
        self.cursor.execute("""
            SELECT current_model from user_info
        """)

        row = self.cursor.fetchone()
        return row[0] if row else ""
