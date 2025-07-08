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
            experiment_series_name TEXT NOT NULL UNIQUE,
            description TEXT DEFAULT '',
    
            -- Simulation configuration
            num_experiments INTEGER DEFAULT 100,
            max_simulation_time FLOAT DEFAULT 10.0,
            
            -- Has Exploded Thresholds
            bounding_box_volume_threshold FLOAT DEFAULT 1.8,
            beam_strain_threshold FLOAT DEFAULT 0.08,
            node_velocity_threshold FLOAT DEFAULT 3.0,

            -- Force configurations (initial is the force applied to the first experiment in the series, final is the last)
                -- the exact force applied to the experiment is in the experiments table
            initial_force_applied_in_y_direction FLOAT,
            final_force_in_y_direction FLOAT,
            initial_force_applied_in_x_direction FLOAT,
            final_force_in_x_direction FLOAT,
            initial_force_applied_in_z_direction FLOAT,
            final_force_in_z_direction FLOAT,
            torsional_force FLOAT,

            -- Braided structure configuration   
            num_strands INTEGER,
            num_layers INTEGER,
            radius FLOAT,
            pitch FLOAT,
            radius_taper FLOAT DEFAULT 0.0, -- Conicity (how much it narrows towards the top)
            material_thickness FLOAT DEFAULT NULL,
            weight_kg FLOAT DEFAULT NULL,
            height_m FLOAT DEFAULT NULL
            
        );
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS experiments (
            -- The experiment_id is not auto-incremented to allow me to set it manually and sort by id later
            -- since the experiments are parallelized, they end up saved out of order otherwise.
            experiment_id INTEGER,
                   
            experiment_series_name TEXT NOT NULL REFERENCES experiment_series(experiment_series_name),                   
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,

            -- Force applied                   
            force_in_x_direction FLOAT,
            force_in_y_direction FLOAT,
            force_in_z_direction FLOAT,
            torsional_force FLOAT,

            -- Has Exploded
            time_to_bounding_box_explosion FLOAT,
            max_bounding_box_volume FLOAT,
            time_to_beam_strain_exceed_explosion FLOAT,
            max_beam_strain FLOAT,
            time_to_node_velocity_spike_explosion FLOAT,
            max_node_velocity FLOAT,
                   
            -- Final Result
            final_height FLOAT
        );
    ''')

    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_experiments_series_name ON experiment_series(experiment_series_name);
    ''')

    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_experiments_experiment_series_name ON experiments(experiment_series_name);
    ''')

    # Insert a default experiment_series record named "default" with 3 experiments.
    cursor.execute('''INSERT OR IGNORE INTO experiment_series 
        (experiment_series_name, description, num_experiments, max_simulation_time, bounding_box_volume_threshold, beam_strain_threshold, node_velocity_threshold, 
        initial_force_applied_in_y_direction, final_force_in_y_direction,
        initial_force_applied_in_x_direction, final_force_in_x_direction,
        initial_force_applied_in_z_direction, final_force_in_z_direction, torsional_force,
        num_strands, num_layers, radius, pitch, radius_taper, material_thickness, weight_kg, height_m) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);''',
        ("_default", "Default configuration", 3, 2.0, 1.8, 0.08, 3.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 5, 10, 0.1, 1.0, 0.0, None, None, None))

    conn.commit()
    close_connection(conn)

    print("Tables created." if not tables_exists else "Table already exists.")



if __name__ == "__main__":
    create_table()
