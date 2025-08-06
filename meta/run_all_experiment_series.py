from database.queries.experiment_series_queries import select_all_experiment_series, update_experiment_series
from database.queries.experiments_queries import delete_experiments_by_series_name
from database.session import SessionLocal
from experiments import run_experiments


###############################################
# Config

experiments_not_to_run = [
    "_default"
]


###############################################


session = SessionLocal()

all_experiment_series = select_all_experiment_series(session)

for experiment_series in all_experiment_series:
    if experiment_series.experiment_series_name in experiments_not_to_run:
        print("Skipping experiment series:", experiment_series.experiment_series_name)
        continue

    experiment_series_name = experiment_series.experiment_series_name
    print(experiment_series_name)

    delete_experiments_by_series_name(session, experiment_series_name) 
    update_experiment_series(session, experiment_series_name, { "is_experiments_outdated": False })
    run_experiments(experiment_series)
    print("Running experiments for series:", experiment_series_name)
