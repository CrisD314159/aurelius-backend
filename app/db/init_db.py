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
        self.user_id = 1

    def _create_tables(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_info (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          name TEXT UNIQUE NOT NULL,
          current_model TEXT NOT NULL       
        )

        """)

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS chats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            title TEXT,
            date_created DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES user_info(id)
        )
        """)

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_interactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id INTEGER,
            user_message TEXT,
            model_message TEXT,
            message_date DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (chat_id) REFERENCES chats(id)
        )
        """)

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_memory_context (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            var TEXT,
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
    """, (self.user_id, name, model))
        self.conn.commit()

    def is_user_registerd(self):
        """
        This method returns the user name 
        to verify if is already registered
        """
        self.cursor.execute("""
        SELECT name FROM user_info WHERE id = ?
    """, (self.user_id,))

        return self.cursor.fetchone()

    def get_user_data(self):
        """
        This method retrieves all the user stored data
        """
        self.cursor.execute("""
        SELECT name, current_model FROM user_info WHERE id = ?
    """, (self.user_id,))

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
    """, (name, model, self.user_id))
        self.conn.commit()

    def save_memory(self, var):
        """
        This method saves an important value for understand better the user
        context
        """
        self.cursor.execute("""
        INSERT INTO user_memory_context (var)
        VALUES (?)
        """, (var,))
        self.conn.commit()

    def load_memory(self):
        """
        This method loads all the memories saved from the user to improve context
        """
        self.cursor.execute("SELECT * FROM user_memory_context")
        rows = self.cursor.fetchall()
        return [row[0] for row in rows]

    def get_user_model(self):
        """
        This method returns de user ollama model to be used
        """
        self.cursor.execute("""
            SELECT current_model from user_info
        """)

        row = self.cursor.fetchone()
        return row[0] if row else ""

    def get_user_chats(self):
        """
            Gets all the chat history from the user
        """
        self.cursor.execute("""
            SELECT * FROM chats WHERE user_id = ?

        """, (self.user_id,))

        rows = self.cursor.fetchall()
        return rows if len(rows) > 0 else []

    def get_chat_content(self, chat_id):
        """
            Gets all the chat content including messages
        """
        self.cursor.execute("""
            SELECT * FROM chat_interactions WHERE chat_id = ?
            ORDER BY message_date ASC

        """, (chat_id, ))

        rows = self.cursor.fetchall()
        return rows

    def create_chat(self, title):
        """
        Creates a new chat
        """
        self.cursor.execute("""
            INSERT INTO chats (user_id, title)
            VALUES(?, ?)

        """, (self.user_id, title,))

        new_id = self.cursor.lastrowid

        self.conn.commit()

        return new_id

    def store_interaction(self, chat_id, user_prompt, llm_answer):
        """
            Stores a new interaction between the user and the llm
        """
        self.cursor.execute("""
        INSERT INTO chat_interactions (chat_id, user_message, model_message)
        VALUES (?, ?, ?)

        """, (chat_id, user_prompt, llm_answer,))
        self.conn.commit()

    def delete_chat(self, chat_id):
        """
        Deletes a chat and its content
        """
        self.cursor.execute("""
            DELETE FROM chat_interactions WHERE chat_id = ?

        """, (chat_id, ))

        self.cursor.execute("""
            DELETE FROM chats WHERE id = ?
        """, (chat_id, ))
        self.conn.commit()
