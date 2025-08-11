from database.queries.experiment_series_queries import delete_experiment_series
from util import delete_experiment_series_folder
from database.session import SessionLocal

experiment_series_names = []

session = SessionLocal()

for experiment_series_name in experiment_series_names:
    delete_experiment_series(session, experiment_series_name)

    delete_experiment_series_folder(experiment_series_name)

