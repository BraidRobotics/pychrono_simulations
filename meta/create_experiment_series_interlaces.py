from sqlalchemy.inspection import inspect
from database.models import ExperimentSeries
from database.queries.experiment_series_queries import insert_experiment_series
from database.session import SessionLocal

num_experiment_series = 9
num_experiments = 100
interlaced_experiment_series_name = "force_no_force_"
group_name = "force_no_force"

initial_model = ExperimentSeries(
    experiment_series_name=interlaced_experiment_series_name + "_00",
    group_name=group_name,
    num_experiments=num_experiments,
    num_strands=4,
    num_layers=3,
    material_thickness=0.005,
    initial_force_applied_in_y_direction=0.0,
    final_force_in_y_direction=-3.0,
    max_simulation_time=20.0,
    reset_force_after_seconds=10.0
)

final_model = ExperimentSeries(
    experiment_series_name=f"{interlaced_experiment_series_name}_{num_experiment_series-1:02d}",
    group_name=group_name,
    num_experiments=num_experiments,
    num_strands=8,
    num_layers=8,
    material_thickness=0.005,
    initial_force_applied_in_y_direction=0.0,
    final_force_in_y_direction=-3.0,
    max_simulation_time=20.0,
    reset_force_after_seconds=10.0
)

session = SessionLocal()

# Save initial model
insert_experiment_series(session, initial_model)

columns = [column.key for column in inspect(ExperimentSeries).mapper.column_attrs if column.key != "experiment_series_name"]

interpolated_models = []
for i in range(1, num_experiment_series):
    values = {}
    for column in columns:
        initial_value = getattr(initial_model, column)
        final_value = getattr(final_model, column)

        if isinstance(initial_value, (int, float)) and isinstance(final_value, (int, float)):
            interpolated = initial_value + (final_value - initial_value) * i / num_experiment_series
            values[column] = int(interpolated / 2) * 2 if column == 'num_strands' else interpolated
        elif initial_value is not None and final_value is not None and initial_value == final_value:
            values[column] = initial_value
        elif initial_value is not None and final_value is not None:
            continue  # skip differing types or non-numeric unequal values
        elif initial_value is not None:
            values[column] = initial_value

    model = ExperimentSeries(
        experiment_series_name=f"{interlaced_experiment_series_name}_{i:02d}",
        **values
    )
    insert_experiment_series(session, model)



# Save final model
insert_experiment_series(session, final_model)
