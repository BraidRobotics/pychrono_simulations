from database.models import ExperimentSeries
from database.queries.experiment_series_queries import insert_experiment_series
from database.session import scoped_session
from experiments import run_non_experiment

if __name__ == '__main__':
    # Configuration
    num_experiments = 48
    group_name = "number_of_strands"
    strand_counts = [2, 4, 6, 8, 10]

    with scoped_session() as session:
        for num_strands in strand_counts:
            series_name = f"number_of_strands__{num_strands:02d}"

            model = ExperimentSeries(
                experiment_series_name=series_name,
                group_name=group_name,
                num_experiments=num_experiments,
                num_strands=num_strands,
                initial_force_applied_in_y_direction=0.0,
                final_force_in_y_direction=-2.4,
                is_experiments_outdated=False,
            )

            insert_experiment_series(session, model)
            print(f"Created: {series_name}")

            run_non_experiment(series_name, will_visualize=False)
            print(f"  ✓ Properties calculated\n")

    print("All experiment series created successfully!")
