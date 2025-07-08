from database import get_connection, close_connection

def select_experiment_by_id(experiment_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT *
        FROM experiments
        WHERE experiment_id = ?;
    ''', (experiment_id,))

    row = cursor.fetchone()
    close_connection(conn)
    return dict(row) if row else None


def select_all_experiments_by_series_name(experiment_series_name):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT *
        FROM experiments
        WHERE experiment_series_name = ?
        ORDER BY experiment_id;
    ''', (experiment_series_name,))

    rows = cursor.fetchall()
    close_connection(conn)
    return rows

def insert_experiment(experiment_id, experiment_series_name, force_in_y_direction, force_in_x_direction, time_to_bounding_box_explosion, max_bounding_box_volume, time_to_beam_strain_exceed_explosion, max_beam_strain, time_to_node_velocity_spike_explosion, max_node_velocity, final_height=None):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO experiments (
            experiment_id,
            experiment_series_name,
            force_in_y_direction,
            force_in_x_direction,
            time_to_bounding_box_explosion,
            max_bounding_box_volume,
            time_to_beam_strain_exceed_explosion,
            max_beam_strain,
            time_to_node_velocity_spike_explosion,
            max_node_velocity,
            final_height
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    ''', (experiment_id, experiment_series_name, force_in_y_direction, force_in_x_direction, time_to_bounding_box_explosion, max_bounding_box_volume, time_to_beam_strain_exceed_explosion, max_beam_strain, time_to_node_velocity_spike_explosion, max_node_velocity, final_height))

    conn.commit()
    close_connection(conn)


def delete_experiments_by_series_name(experiment_series_name):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        DELETE FROM experiments
        WHERE experiment_series_name = ?;
    ''', (experiment_series_name,))

    conn.commit()
    close_connection(conn)
