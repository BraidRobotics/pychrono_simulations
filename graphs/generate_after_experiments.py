from pathlib import Path
import traceback

from database.queries.experiments_queries import select_all_experiments_by_series_name
from database.session import SessionLocal
from .series_graphs import (
    generate_experiment_series_force_graph,
    generate_experiment_series_height_graph,
    generate_experiment_series_elastic_recovery_graph
)


def generate_graphs_after_experiments(experiment_series):
    safe_name = experiment_series.experiment_series_name.replace('/', '_').replace(' ', '_')
    delete_relevant_graphs(safe_name)

    session = SessionLocal()
    try:
        experiments = select_all_experiments_by_series_name(session, experiment_series.experiment_series_name)

        generate_experiment_series_force_graph(session, safe_name, experiments)
        generate_experiment_series_height_graph(session, safe_name, experiments, experiment_series.height_m)
        generate_experiment_series_elastic_recovery_graph(session, safe_name, experiments, experiment_series.reset_force_after_seconds, experiment_series.height_m)
    finally:
        session.close()


def delete_relevant_graphs(safe_name):
    graphs_dir = Path(__file__).parent.parent / "experiments_server" / "assets" / "graphs"

    if graphs_dir.exists():
        # Delete only series-specific graphs
        (graphs_dir / f"series_{safe_name}_force.html").unlink(missing_ok=True)
        (graphs_dir / f"series_{safe_name}_height.html").unlink(missing_ok=True)
        (graphs_dir / f"series_{safe_name}_elastic_recovery.html").unlink(missing_ok=True)
    else:
        graphs_dir.mkdir(parents=True, exist_ok=True)