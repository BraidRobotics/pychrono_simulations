from experiments import run_non_experiment
from database.queries.experiment_series_queries import select_all_experiment_series
from database.session import SessionLocal

if __name__ == '__main__':
    session = SessionLocal()
    all_experiment_series = select_all_experiment_series(session)
    try:
        for experiment_series in all_experiment_series:
            run_non_experiment(experiment_series, will_visualize=False)
    finally:
        session.close()