from sqlalchemy.inspection import inspect
from database.models import ExperimentSeries
from database.queries.experiment_series_queries import insert_experiment_series
from database.session import scoped_session
from experiments import run_non_experiment

if __name__ == '__main__':
    # Configuration
    num_experiment_series = 7
    num_experiments = 48
    interlaced_experiment_series_name = "number_of_layers__"
    group_name = "number_of_layers"
    initial_num_layers = 2
    final_num_layers = 8

    # Create initial and final models for interpolation
    initial_model = ExperimentSeries(
        experiment_series_name=f"{interlaced_experiment_series_name}{initial_num_layers:02d}",
        group_name=group_name,
        num_experiments=num_experiments,
        num_layers=initial_num_layers,
        initial_force_applied_in_y_direction=0.0,
        final_force_in_y_direction=-1.7,
        is_experiments_outdated=False,
    )

    final_model = ExperimentSeries(
        experiment_series_name=f"{interlaced_experiment_series_name}{final_num_layers:02d}",
        group_name=group_name,
        num_experiments=num_experiments,
        num_layers=final_num_layers,
        initial_force_applied_in_y_direction=-0.0,
        final_force_in_y_direction=-2.2,
        is_experiments_outdated=False,
    )

    columns = [column.key for column in inspect(ExperimentSeries).mapper.column_attrs if column.key != "experiment_series_name"]

    with scoped_session() as session:
        # Create initial model
        insert_experiment_series(session, initial_model)
        print(f"Created: {initial_model.experiment_series_name}")
        run_non_experiment(initial_model.experiment_series_name, will_visualize=False)
        print(f"  ✓ Properties calculated\n")

        # Create interpolated models
        for i in range(1, num_experiment_series - 1):
            values = {}
            for column in columns:
                initial_value = getattr(initial_model, column)
                final_value = getattr(final_model, column)

                if isinstance(initial_value, (int, float)) and isinstance(final_value, (int, float)):
                    values[column] = initial_value + (final_value - initial_value) * i / (num_experiment_series - 1)
                elif initial_value is not None and final_value is not None and initial_value == final_value:
                    values[column] = initial_value
                elif initial_value is not None and final_value is not None:
                    continue
                elif initial_value is not None:
                    values[column] = initial_value

            num_layers_val = int(initial_num_layers + (final_num_layers - initial_num_layers) * i / (num_experiment_series - 1))

            model = ExperimentSeries(
                experiment_series_name=f"{interlaced_experiment_series_name}{num_layers_val:02d}",
                is_experiments_outdated=False,
                **values
            )

            insert_experiment_series(session, model)
            print(f"Created: {model.experiment_series_name}")
            run_non_experiment(model.experiment_series_name, will_visualize=False)
            print(f"  ✓ Properties calculated\n")

        # Create final model
        insert_experiment_series(session, final_model)
        print(f"Created: {final_model.experiment_series_name}")
        run_non_experiment(final_model.experiment_series_name, will_visualize=False)
        print(f"  ✓ Properties calculated\n")

    print("All experiment series created successfully!")
