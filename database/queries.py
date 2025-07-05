from database import get_connection, close_connection

def select_experiment_series_by_id(experiment_series_name):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT id FROM experiment_series WHERE experiment_series_name = ?', (experiment_series_name,))
    row = cursor.fetchone()

    close_connection(conn)
    return row[0] if row else None


def select_experiments_by_series_id(experiment_series_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT id, timestamp, time_to_bounding_box_explosion, time_to_beam_strain_exceed_explosion, time_to_node_velocity_spike_explosion
        FROM experiments
        WHERE experiment_series_id = ?
        ORDER BY timestamp DESC
    ''', (experiment_series_id,))

    rows = cursor.fetchall()
    close_connection(conn)
    return rows

def insert_experiment(experiment_series_id, time_to_bounding_box_explosion, time_to_beam_strain_exceed_explosion, time_to_node_velocity_spike_explosion):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO experiments (experiment_series_id, time_to_bounding_box_explosion, time_to_beam_strain_exceed_explosion, time_to_node_velocity_spike_explosion)
        VALUES (?, ?, ?, ?)
    ''', (experiment_series_id, time_to_bounding_box_explosion, time_to_beam_strain_exceed_explosion, time_to_node_velocity_spike_explosion))

    conn.commit()
    close_connection(conn)
    print("Experiment inserted successfully.")



