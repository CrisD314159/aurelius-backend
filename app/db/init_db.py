"""
This module contains local database initialization for Aurelius app
"""
import sqlite3
import os
import sys
from pathlib import Path


def get_app_data_dir():
    """
    Gets the correct path for database init in dev and in pyinstaller
    """
    if getattr(sys, 'frozen', False):
        if sys.platform == "win32":
            # Windows: C:\Users\USERNAME\AppData\Local\Aurelius
            app_data = os.getenv('LOCALAPPDATA')
            app_dir = Path(app_data) / "Aurelius"
        elif sys.platform == "darwin":
            # macOS: ~/Library/Application Support/Aurelius
            app_dir = Path.home() / "Library" / "Application Support" / "Aurelius"
        else:
            # Linux: ~/.local/share/Aurelius
            app_dir = Path.home() / ".local" / "share" / "Aurelius"
    else:
        # dev mode
        app_dir = Path(__file__).parent

    # Create directory if it does not exists
    app_dir.mkdir(parents=True, exist_ok=True)
    return app_dir


def get_database_path():
    """
    Obtiene la ruta completa a la base de datos
    Prioriza la variable de entorno DATABASE_PATH si está definida (útil para Electron)
    """
    env_db_path = os.getenv('DATABASE_PATH')
    if env_db_path:
        # Make sure parent directory already exists
        os.makedirs(os.path.dirname(env_db_path), exist_ok=True)
        return env_db_path

    # otherwise, create parent directory
    app_dir = get_app_data_dir()
    db_path = app_dir / "aurelius.db"

    print(f"[DB] Database location: {db_path}")
    print(f"[DB] Directory writable: {os.access(app_dir, os.W_OK)}")

    return str(db_path)


class AureliusDB:
    """
    This class contains database initialization methods 
    """

    def __init__(self, db_path=None):
        """
        Inicializa la conexión a la base de datos.

        Args:
            db_path: Ruta personalizada a la BD. Si es None, usa la ubicación automática.
        """
        if db_path is None:
            db_path = get_database_path()

        db_dir = os.path.dirname(db_path)
        if not os.access(db_dir, os.W_OK):
            raise PermissionError(
                f"No write permission in database directory: {db_dir}"
            )

        try:
            self.conn = sqlite3.connect(
                db_path,
                check_same_thread=False,
                timeout=10.0
            )
            # Habilitar Write-Ahead Logging para mejor concurrencia
            self.conn.execute("PRAGMA journal_mode=WAL")
            # Habilitar foreign keys
            self.conn.execute("PRAGMA foreign_keys=ON")

            self.cursor = self.conn.cursor()
            self.user_id = 1

            print(f"[DB] Connected successfully to: {db_path}")
            self._create_tables()

        except sqlite3.OperationalError as e:
            raise sqlite3.OperationalError(
                f"Failed to open database at {db_path}. Error: {e}"
            )

    def _create_tables(self):
        """Crea las tablas si no existen"""
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
        print("[DB] Tables created/verified successfully")

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
            current_model = ? 
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
        return [row[1] for row in rows]

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
        chats_dict = []
        if len(rows) > 0:
            for row in rows:
                chats_dict.append({
                    "chat_id": row[0],
                    "user_id": row[1],
                    "title": row[2],
                    "date_created": row[3]
                })
        return chats_dict

    def get_chat_content(self, chat_id):
        """
        Gets all the chat content including messages
        """
        self.cursor.execute("""
            SELECT * FROM chat_interactions WHERE chat_id = ?
            ORDER BY message_date ASC
        """, (chat_id, ))

        rows = self.cursor.fetchall()
        messages = []

        if len(rows) > 0:
            for row in rows:
                messages.append({
                    "interaction_id": row[0],
                    "chat_id": row[1],
                    "user_message": row[2],
                    "model_message": row[3],
                    "message_date": row[4]
                })
        return messages

    def get_chat_content_ollama(self, chat_id):
        """
        Gets all the chat content including messages in ollama format
        """
        self.cursor.execute("""
            SELECT * FROM chat_interactions WHERE chat_id = ?
            ORDER BY message_date ASC
        """, (chat_id, ))

        rows = self.cursor.fetchall()
        messages = []

        if len(rows) > 0:
            for row in rows:
                messages.append({"role": "user", "content": row[2]})
                messages.append({"role": "assistant", "content": row[3]})
        return messages

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

        new_interaction_id = self.cursor.lastrowid
        self.conn.commit()

        self.cursor.execute("""
            SELECT message_date from chat_interactions WHERE id = ?
        """, (new_interaction_id,))
        row = self.cursor.fetchone()

        return {
            "id": new_interaction_id,
            "chat_id": chat_id,
            "user_message": user_prompt,
            "model_message": llm_answer,
            "message_date": row[0] if row else None
        }

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

    def close(self):
        """
        Cierra la conexión a la base de datos
        """
        if self.conn:
            self.conn.close()
            print("[DB] Connection closed")

    def __enter__(self):
        """Context manager support"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager support"""
        self.close()


# Para debugging - ejecutar directamente este módulo
if __name__ == "__main__":
    print("Testing database initialization...")
    print(f"Frozen: {getattr(sys, 'frozen', False)}")
    print(f"Platform: {sys.platform}")
    print(f"Database path: {get_database_path()}")

    try:
        db = AureliusDB()
        print("✓ Database initialized successfully")
        db.close()
    except Exception as e:
        print(f"✗ Error: {e}")
