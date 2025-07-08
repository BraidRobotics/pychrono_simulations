from database import get_connection, close_connection

def select_all_experiment_series():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''SELECT * FROM experiment_series ORDER BY experiment_series_name;''')
    rows = cursor.fetchall()

    close_connection(conn)
    return [dict(row) for row in rows]

def select_experiment_series_by_name(experiment_series_name):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM experiment_series WHERE experiment_series_name = ?;', (experiment_series_name,))
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
    description = ""

    cursor.execute('''
        INSERT INTO experiment_series (
            experiment_series_name, description,
            num_experiments, max_simulation_time,
            bounding_box_volume_threshold, beam_strain_threshold, node_velocity_threshold,
            initial_force_applied_in_y_direction, final_force_in_y_direction,
            initial_force_applied_in_x_direction, final_force_in_x_direction,
            initial_force_applied_in_z_direction, final_force_in_z_direction,
            torsional_force,
            num_strands, num_layers, radius, pitch, radius_taper,
            material_thickness, weight_kg, height_m,
            is_experiments_outdated
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        RETURNING *;
    ''', (
        experiment_series_name, description,
        num_experiments, max_simulation_time,
        1.8, 0.08, 3.0,
        0.0, 0.0,
        0.0, 0.0,
        0.0, 0.0,
        0.0,
        5, 10, 0.15, 1.13, 0.0,
        None, None, None,
        False
    ))

    row = cursor.fetchone()
    conn.commit()
    close_connection(conn)
    return dict(row)

def update_experiment_series(experiment_series_name, updates):
    if not updates:
        return

    conn = get_connection()
    cursor = conn.cursor()

    set_clause = ', '.join([f"{field} = ?" for field in updates])
    values = list(updates.values()) + [experiment_series_name]

    cursor.execute(f'''
        UPDATE experiment_series
        SET {set_clause}
        WHERE experiment_series_name = ?
        RETURNING *;
    ''', values)

    updated_row = cursor.fetchone()
    conn.commit()
    close_connection(conn)

    return dict(updated_row) if updated_row else None

def delete_experiment_series(experiment_series_name):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('DELETE FROM experiments WHERE experiment_series_name = ?;', (experiment_series_name,))

    cursor.execute('DELETE FROM experiment_series WHERE experiment_series_name = ?;', (experiment_series_name,))

    conn.commit()
    close_connection(conn)
