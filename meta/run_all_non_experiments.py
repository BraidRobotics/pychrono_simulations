from experiments import run_non_experiment
from database.queries.experiment_series_queries import select_all_experiment_series
from database.session import scoped_session

if __name__ == '__main__':
    with scoped_session() as session:
        all_experiment_series = select_all_experiment_series(session)
        for experiment_series in all_experiment_series:
            run_non_experiment(experiment_series, will_visualize=False)