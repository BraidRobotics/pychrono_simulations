from database import get_connection, close_connection


def create_table():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE name='experiments'")
    experiments_table_exists = cursor.fetchone() is not None

    cursor.execute("SELECT name FROM sqlite_master WHERE name='experiment_series'")
    series_table_exists = cursor.fetchone() is not None

    tables_exists = experiments_table_exists and series_table_exists

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS experiment_series (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            experiment_series_name TEXT NOT NULL UNIQUE,
            description TEXT DEFAULT '',
       
            num_experiments INTEGER DEFAULT 100,
            max_simulation_time FLOAT DEFAULT 10.0,
            
            force_type TEXT CHECK(force_type IN ('TOP_NODES_DOWN', 'ALL_NODES_DOWN', 'RIGHT_SIDE_SIDEWAYS')),
            initial_force_applied_in_y_direction FLOAT,
            initial_force_applied_in_x_direction FLOAT,
            force_increment FLOAT,
                   
            num_strands INTEGER,
            num_layers INTEGER,
            radius FLOAT,
            pitch FLOAT
        );
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS experiments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            experiment_series_id INTEGER NOT NULL,
                   
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,

            time_to_bounding_box_explosion FLOAT,
            time_to_beam_strain_exceed_explosion FLOAT,
            time_to_node_velocity_spike_explosion FLOAT,
                    
            FOREIGN KEY (experiment_series_id) REFERENCES experiment_series(id)
        );
    ''')

    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_experiments_series_id ON experiments(experiment_series_id);
    ''')

    conn.commit()
    close_connection(conn)

    print("Tables created." if not tables_exists else "Table already exists.")



if __name__ == "__main__":
    create_table()
