from database.models import ExperimentSeries
from database.queries.experiment_series_queries import insert_experiment_series, delete_experiment_series
from database.session import scoped_session
from experiments import run_non_experiment
from util import delete_experiment_series_folder

if __name__ == '__main__':
    # Configuration
    num_experiments = 48
    group_name = "force_no_force"
    strand_radius = 0.007

    # 15 configurations: 5 strand values × 3 layer values
    strand_values = [4, 6, 8, 10, 12]
    layer_values = [2, 3, 4]

    # Force optimized per strand count to achieve 10-15% compression
    force_by_strands = {
        4: -2.5,   # Already good at 18% max compression
        6: -4.5,   # Increase from 2.5N to get ~10-15% compression
        8: -7.0,   # Increase significantly (was barely compressing)
        10: -9.0,  # Very stiff, needs high force
        12: -11.0  # Extremely stiff, needs very high force
    }

    # Delete all existing series in this group
    with scoped_session() as session:
        existing_series = session.query(ExperimentSeries).filter_by(group_name=group_name).all()
        if existing_series:
            print(f"Deleting {len(existing_series)} existing series in group '{group_name}'...")
            for series in existing_series:
                delete_experiment_series(session, series.experiment_series_name)
                delete_experiment_series_folder(series.experiment_series_name)
                print(f"  Deleted: {series.experiment_series_name}")
            print()

    # Create new series
    with scoped_session() as session:
        for num_strands in strand_values:
            for num_layers in layer_values:
                series_name = f"force_no_force_{num_strands}_strands_{num_layers}_layers"
                final_force = force_by_strands[num_strands]

                model = ExperimentSeries(
                    experiment_series_name=series_name,
                    group_name=group_name,
                    num_experiments=num_experiments,
                    num_strands=num_strands,
                    num_layers=num_layers,
                    strand_radius=strand_radius,
                    initial_force_applied_in_y_direction=0.0,
                    final_force_in_y_direction=final_force,
                    max_simulation_time=15.0,
                    reset_force_after_seconds=10.0,
                    is_experiments_outdated=False,
                )

                insert_experiment_series(session, model)
                print(f"Created: {series_name} (force: {final_force}N)")

                run_non_experiment(series_name, will_visualize=False)
                print(f"  ✓ Properties calculated\n")

    print("All 15 experiment series created successfully!")
