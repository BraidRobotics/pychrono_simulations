from database import get_connection, close_connection

def insert_experiment(experiment_name, description, time_to_explosion, force_applied, force_type, braided_structure_config, meta_data):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO experiments (experiment_name, description, time_to_explosion, force_applied, force_type, meta_data)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (experiment_name, description, time_to_explosion, force_applied, force_type, meta_data))

    conn.commit()
    close_connection(conn)

    print("Experiment inserted successfully.", experiment_name, description, time_to_explosion, force_applied, force_type, braided_structure_config, meta_data)

