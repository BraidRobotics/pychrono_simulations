"""Direct test script to see explosion behavior without multiprocessing"""
import sys
from database.session import scoped_session
from database.queries.experiment_series_queries import select_experiment_series_by_name
from experiments.experiment import experiment_loop
from config import ExperimentConfig

if __name__ == '__main__':
    with scoped_session() as session:
        series = select_experiment_series_by_name(session, 'single_explosion_simulation')

        if not series:
            print("Series 'single_explosion_simulation' not found!")
            sys.exit(1)

        print(f"Running {series.experiment_series_name}")
        print(f"Force: {series.final_force_in_y_direction}N")
        print(f"Thresholds: bbox={series.bounding_box_volume_threshold}, "
              f"strain={series.beam_strain_threshold}, vel={series.node_velocity_threshold}")
        print("-" * 60)

        config = ExperimentConfig(
            experiment_id=1,
            force_in_y_direction=series.final_force_in_y_direction,
            force_in_x_direction=0.0,
            force_in_z_direction=0.0,
            force_top_nodes_in_y_direction=0.0,
            torsional_force=0.0,
            will_visualize=True,
            will_record_video=False,
            max_simulation_time=10.0,
            run_forever=False
        )

        # Run directly without multiprocessing
        experiment_loop(series, config)
