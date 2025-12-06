import subprocess
from database.session import scoped_session
from database.queries.experiment_series_queries import select_all_experiment_series
from graphs.generate_after_experiments import generate_graphs_after_experiments

if __name__ == "__main__":
    with scoped_session() as session:
        experiment_series_list = select_all_experiment_series(session)
        for experiment_series in experiment_series_list:
            generate_graphs_after_experiments(experiment_series)

    subprocess.run(["python", "-m", "meta.generate_aggregate_graphs"])
