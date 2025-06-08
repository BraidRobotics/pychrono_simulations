import sqlite3
import os


def get_connection():
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # This allows us to access columns by name
    return conn


def close_connection(conn):
    if conn:
        conn.close()
    else:
        print("Connection is already closed or was never opened.")


