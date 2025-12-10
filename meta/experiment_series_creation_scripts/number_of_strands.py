import sys
from database.models import ExperimentSeries
from database.queries.experiment_series_queries import insert_experiment_series
from database.session import scoped_session
from experiments import run_non_experiment

# Configuration
num_experiments = 48
group_name = "number_of_strands"
strand_counts = [4, 6, 8, 10]

# Validate that all strand counts are even
errors = []
for num_strands in strand_counts:
    if num_strands % 2 != 0:
        errors.append(f"Number of strands ({num_strands}) must be even for symmetry.")
    if num_strands < 2:
        errors.append(f"Number of strands ({num_strands}) must be at least 2.")

if errors:
    print("ERROR: Invalid configuration values:")
    for error in errors:
        print(f"  - {error}")
    sys.exit(1)

# Create experiment series
print("Creating experiment series...")
with scoped_session() as session:
    created_series = []

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
        created_series.append(series_name)
        print(f"Created: {series_name}")

# Run non-experiments
print("\nRunning non-experiments to generate images and calculate properties...")
with scoped_session() as session:
    for series_name in created_series:
        series = session.query(ExperimentSeries).filter_by(experiment_series_name=series_name).first()
        if series:
            print(f"Running non-experiment for: {series_name}")
            run_non_experiment(series_name, will_visualize=False)

print("\nAll experiment series created and non-experiments completed!")
