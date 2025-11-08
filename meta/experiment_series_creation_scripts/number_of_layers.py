from sqlalchemy.inspection import inspect
from database.models import ExperimentSeries
from database.queries.experiment_series_queries import insert_experiment_series
from database.session import SessionLocal

num_experiment_series = 6
num_experiments = 48
interlaced_experiment_series_name = "number_of_layers_"
group_name = "number_of_layers"

# num layers = 2, 3, 4, 5, 6, 7, 8

initial_model = ExperimentSeries(
    experiment_series_name=interlaced_experiment_series_name + "_00",
    group_name=group_name,
    num_experiments=num_experiments,
    num_layers=2,
    initial_force_applied_in_y_direction=0.0,
    final_force_in_y_direction=-1.7,
)

final_model = ExperimentSeries(
    experiment_series_name=f"{interlaced_experiment_series_name}_{num_experiment_series:02d}",
    group_name=group_name,
    num_experiments=num_experiments,
    num_layers=8,
    initial_force_applied_in_y_direction=-0.0,
    final_force_in_y_direction=-1.7,
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
            values[column] = initial_value + (final_value - initial_value) * i / num_experiment_series
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
