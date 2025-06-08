from database import get_connection, close_connection

def insert_experiment(experiment_name, description, time_to_explosion, force_applied_in_y_direction, force_applied_in_x_direction, force_type, meta_data, max_simulation_time):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO experiments (experiment_name, description, time_to_explosion, force_applied_in_y_direction, force_applied_in_x_direction, force_type, meta_data, max_simulation_time)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (experiment_name, description, time_to_explosion, force_applied_in_y_direction, force_applied_in_x_direction, force_type, meta_data, max_simulation_time))

    conn.commit()
    close_connection(conn)

    print("Experiment inserted successfully.", experiment_name, description, time_to_explosion, force_applied_in_y_direction, force_applied_in_x_direction, force_type, meta_data, max_simulation_time)
