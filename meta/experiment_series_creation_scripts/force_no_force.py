import sys
from database.models import ExperimentSeries
from database.queries.experiment_series_queries import insert_experiment_series
from database.session import scoped_session
from experiments import run_non_experiment

# Factorial design: 3 strand values × 3 layer values = 9 experiment series
num_experiments = 46
interlaced_experiment_series_name = "force_no_force_"
group_name = "force_no_force"

# Define factorial grid
strand_values = [4, 6, 8]  # All divisible by 2
layer_values = [3, 5, 7]   # Low, medium, high
strand_radius = 0.007  # Constant

# Validate configuration before proceeding
errors = []
for num_strands in strand_values:
    if num_strands % 2 != 0:
        errors.append(f"num_strands ({num_strands}) must be divisible by 2 for symmetry.")
    if num_strands < 2:
        errors.append(f"num_strands ({num_strands}) must be at least 2.")

for num_layers in layer_values:
    if num_layers < 2:
        errors.append(f"num_layers ({num_layers}) must be at least 2.")

if strand_radius <= 0:
    errors.append(f"strand_radius ({strand_radius}) must be greater than 0.")

if errors:
    print("ERROR: Invalid configuration values:")
    for error in errors:
        print(f"  - {error}")
    sys.exit(1)

with scoped_session() as session:
    # Create all combinations
    series_index = 0
    for num_strands in strand_values:
        for num_layers in layer_values:
            model = ExperimentSeries(
                experiment_series_name=f"{interlaced_experiment_series_name}{series_index:02d}",
                group_name=group_name,
                num_experiments=num_experiments,
                num_strands=num_strands,
                num_layers=num_layers,
                strand_radius=strand_radius,
                initial_force_applied_in_y_direction=0.0,
                final_force_in_y_direction=-3.0,
                max_simulation_time=20.0,
                reset_force_after_seconds=10.0,
                is_experiments_outdated=False,
            )

            # Save model (validation happens automatically)
            insert_experiment_series(session, model)
            print(f"Created: {model.experiment_series_name}")
            series_index += 1

print("\nRunning non-experiments to generate images and calculate properties...")
with scoped_session() as session:
    series_index = 0
    for num_strands in strand_values:
        for num_layers in layer_values:
            series_name = f"{interlaced_experiment_series_name}{series_index:02d}"
            series = session.query(ExperimentSeries).filter_by(experiment_series_name=series_name).first()
            if series:
                print(f"Running non-experiment for: {series_name}")
                run_non_experiment(series_name, will_visualize=False)
            series_index += 1

print("\nAll experiment series created and non-experiments completed!")
