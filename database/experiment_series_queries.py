from database import get_connection, close_connection

def select_all_experiment_series():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT
            id, experiment_series_name, description,
            num_experiments, max_simulation_time,
            force_type, initial_force_applied_in_y_direction, initial_force_applied_in_x_direction,
            force_increment,
            num_strands, num_layers, radius, pitch
        FROM experiment_series
        ORDER BY id;
    ''')
    rows = cursor.fetchall()

    close_connection(conn)
    return [dict(row) for row in rows]

def select_experiment_series_by_name(experiment_series_name):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT
            id, experiment_series_name, description,
            num_experiments, max_simulation_time,
            force_type, initial_force_applied_in_y_direction, initial_force_applied_in_x_direction,
            force_increment,
            num_strands, num_layers, radius, pitch
        FROM experiment_series
        WHERE experiment_series_name = ?;
    ''', (experiment_series_name,))
    row = cursor.fetchone()

    close_connection(conn)
    return dict(row) if row else None


def is_experiment_series_name_unique(experiment_series_name):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT COUNT(*) FROM experiment_series WHERE experiment_series_name = ?;', (experiment_series_name,))
    count = cursor.fetchone()[0]

    close_connection(conn)
    return count == 0  # Returns True if unique, False if not unique


def insert_experiment_series(experiment_series_name):
    conn = get_connection()
    cursor = conn.cursor()

    ## default values
    num_experiments = 100
    max_simulation_time = 10.0
    force_type = "TOP_NODES_DOWN"
    initial_force_applied_in_y_direction = 0.0
    initial_force_applied_in_x_direction = 0.0
    force_increment = 0.1
    num_strands = 5
    num_layers = 10
    radius = 0.15
    pitch = 1.13
    description = ""

    cursor.execute('''
        INSERT INTO experiment_series (
            experiment_series_name, description,
            num_experiments, max_simulation_time,
            force_type, initial_force_applied_in_y_direction, initial_force_applied_in_x_direction,
            force_increment,
            num_strands, num_layers, radius, pitch
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    ''', (
        experiment_series_name, description,
        num_experiments, max_simulation_time,
        force_type, initial_force_applied_in_y_direction, initial_force_applied_in_x_direction,
        force_increment,
        num_strands, num_layers, radius, pitch
    ))

    conn.commit()
    close_connection(conn)
    return cursor.lastrowid

def update_experiment_series(experiment_series_id, updates):
    if not updates:
        return

    conn = get_connection()
    cursor = conn.cursor()

    for field, value in updates.items():
        cursor.execute(f'''
            UPDATE experiment_series
            SET {field} = ?
            WHERE id = ?;
        ''', (value, experiment_series_id))

    conn.commit()
    close_connection(conn)
    print(f"Experiment series {experiment_series_id} updated successfully with fields: {list(updates.keys())}")

def delete_experiment_series(experiment_series_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('DELETE FROM experiments WHERE experiment_series_id = ?;', (experiment_series_id,))

    cursor.execute('DELETE FROM experiment_series WHERE id = ?;', (experiment_series_id,))

    conn.commit()
    close_connection(conn)

    print(f"Experiment series {experiment_series_id} and its experiments deleted successfully.")