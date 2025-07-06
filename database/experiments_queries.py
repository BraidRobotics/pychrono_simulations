from database import get_connection, close_connection


def select_all_experiments_by_series_id(experiment_series_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT *
        FROM experiments
        WHERE experiment_series_id = ?
    ''', (experiment_series_id,))

    rows = cursor.fetchall()
    close_connection(conn)
    return rows

def insert_experiment(experiment_series_id, time_to_bounding_box_explosion, time_to_beam_strain_exceed_explosion, time_to_node_velocity_spike_explosion):
    conn = get_connection()
    cursor = conn.cursor()

    print("****************", experiment_series_id)

    cursor.execute('''
        INSERT INTO experiments (experiment_series_id, time_to_bounding_box_explosion, time_to_beam_strain_exceed_explosion, time_to_node_velocity_spike_explosion)
        VALUES (?, ?, ?, ?);
    ''', (experiment_series_id, time_to_bounding_box_explosion, time_to_beam_strain_exceed_explosion, time_to_node_velocity_spike_explosion))

    conn.commit()
    close_connection(conn)
    print("Experiment inserted successfully.")


def delete_experiments_by_series_id(experiment_series_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        DELETE FROM experiments
        WHERE experiment_series_id = ?;
    ''', (experiment_series_id,))

    conn.commit()
    close_connection(conn)
    print(f"All experiments in series {experiment_series_id} deleted successfully.")