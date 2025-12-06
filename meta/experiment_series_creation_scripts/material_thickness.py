import sys
from sqlalchemy.inspection import inspect
from database.models import ExperimentSeries
from database.queries.experiment_series_queries import insert_experiment_series
from database.session import scoped_session
from experiments import run_non_experiment

num_experiment_series = 6
num_experiments = 24
interlaced_experiment_series_name = "strand_thickness_experiment_"

# Configuration values
initial_strand_radius = 0.003
final_strand_radius = 0.008

# Validate configuration before proceeding
errors = []
if initial_strand_radius <= 0:
    errors.append(f"Initial strand_radius ({initial_strand_radius}) must be greater than 0.")
if final_strand_radius <= 0:
    errors.append(f"Final strand_radius ({final_strand_radius}) must be greater than 0.")
if initial_strand_radius >= final_strand_radius:
    errors.append(f"Initial strand_radius ({initial_strand_radius}) must be less than final strand_radius ({final_strand_radius}).")

if errors:
    print("ERROR: Invalid configuration values:")
    for error in errors:
        print(f"  - {error}")
    sys.exit(1)

initial_model = ExperimentSeries(
    experiment_series_name=interlaced_experiment_series_name + "_01",
    group_name="strand_thickness",
    num_experiments=num_experiments,
    strand_radius=initial_strand_radius,
    initial_force_applied_in_y_direction=0.0,
    final_force_in_y_direction=-4.0,
    is_experiments_outdated=False,
)

final_model = ExperimentSeries(
    experiment_series_name=f"{interlaced_experiment_series_name}_{num_experiment_series:02d}",
    group_name="strand_thickness",
    num_experiments=num_experiments,
    strand_radius=final_strand_radius,
    initial_force_applied_in_y_direction=0.0,
    final_force_in_y_direction=-4.0,
    is_experiments_outdated=False,
)

with scoped_session() as session:
    # Save initial model (validation happens automatically)
    insert_experiment_series(session, initial_model)
    print(f"Created: {initial_model.experiment_series_name}")

    columns = [column.key for column in inspect(ExperimentSeries).mapper.column_attrs if column.key != "experiment_series_name"]

    # Create and save interpolated models
    for i in range(2, num_experiment_series):
        values = {}
        for column in columns:
            initial_value = getattr(initial_model, column)
            final_value = getattr(final_model, column)

            if isinstance(initial_value, (int, float)) and isinstance(final_value, (int, float)):
                values[column] = initial_value + (final_value - initial_value) * i / num_experiment_series
            elif initial_value is not None and final_value is not None and initial_value == final_value:
                values[column] = initial_value
            elif initial_value is not None and final_value is not None:
                continue  # skip differing types or non-numeric unequal values
            elif initial_value is not None:
                values[column] = initial_value

        model = ExperimentSeries(
            experiment_series_name=f"{interlaced_experiment_series_name}_{i:02d}",
            is_experiments_outdated=False,
            **values
        )

        # Save model (validation happens automatically)
        insert_experiment_series(session, model)
        print(f"Created: {model.experiment_series_name}")

    # Save final model (validation happens automatically)
    insert_experiment_series(session, final_model)
    print(f"Created: {final_model.experiment_series_name}")

print("\nRunning non-experiments to generate images and calculate properties...")
with scoped_session() as session:
    all_series_names = [initial_model.experiment_series_name]
    all_series_names.extend([f"{interlaced_experiment_series_name}_{i:02d}" for i in range(2, num_experiment_series)])
    all_series_names.append(final_model.experiment_series_name)

    for series_name in all_series_names:
        series = session.query(ExperimentSeries).filter_by(experiment_series_name=series_name).first()
        if series:
            print(f"Running non-experiment for: {series_name}")
            run_non_experiment(series_name, will_visualize=False)

print("\nAll experiment series created and non-experiments completed!")
