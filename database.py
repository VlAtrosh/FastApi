import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "products.db")

def get_connection():
    """Получение соединения с БД"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Возвращает строки как словари
    return conn

def init_db():
    """Инициализация базы данных"""
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                name      TEXT    UNIQUE NOT NULL,
                price     INTEGER NOT NULL CHECK(price >= 0),
                in_stock  BOOLEAN DEFAULT 1 NOT NULL
            )
        """)
        conn.commit()
