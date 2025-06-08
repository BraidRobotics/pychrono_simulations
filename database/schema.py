from database import get_connection, close_connection


def create_table():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='experiments'")
    table_exists = cursor.fetchone() is not None

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS experiments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            experiment_name TEXT NOT NULL,
            description TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            time_to_explosion FLOAT,
            force_applied FLOAT,
            force_type TEXT CHECK(force_type IN ('TOP_NODES_DOWN', 'ALL_NODES_DOWN', 'RIGHT_SIDE_SIDEWAYS')),
            braided_structure_config TEXT,
            meta_data TEXT
        )
    ''')

    conn.commit()
    close_connection(conn)

    print("Table created." if not table_exists else "Table already exists.")



if __name__ == "__main__":
    create_table()
