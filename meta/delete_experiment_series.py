from database.models import ExperimentSeries
from database.queries.experiment_series_queries import delete_experiment_series
from util import delete_experiment_series_folder
from database.session import SessionLocal

experiment_series_names = [
]

experiment_series_group_names = [
    "force_no_force",
]

session = SessionLocal()

# Delete individual series by name
for experiment_series_name in experiment_series_names:
    delete_experiment_series(session, experiment_series_name)
    delete_experiment_series_folder(experiment_series_name)
    print(f"Deleted: {experiment_series_name}")

# Delete all series in specified groups
for group_name in experiment_series_group_names:
    series_in_group = session.query(ExperimentSeries).filter_by(group_name=group_name).all()
    if series_in_group:
        print(f"\nDeleting {len(series_in_group)} series in group '{group_name}':")
        for series in series_in_group:
            delete_experiment_series(session, series.experiment_series_name)
            delete_experiment_series_folder(series.experiment_series_name)
            print(f"  Deleted: {series.experiment_series_name}")
    else:
        print(f"\nNo series found in group '{group_name}'")

session.close()
print("\nDone!")
