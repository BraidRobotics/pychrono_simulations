from database.queries.experiments_queries import select_all_experiments_by_series_name
from database.session import SessionLocal
from .aggregate_graphs import generate_load_capacity_ratio_graph, generate_material_thickness_weight_graph
from .series_graphs import generate_experiment_series_force_graph, generate_experiment_series_height_graph


def generate_graphs_after_experiments(experiment_series):
    session = SessionLocal()
    try:
        experiments = select_all_experiments_by_series_name(session, experiment_series.experiment_series_name)

        generate_experiment_series_force_graph(session, experiment_series.experiment_series_name, experiments)
        generate_experiment_series_height_graph(session, experiment_series.experiment_series_name, experiments, experiment_series.height_m)

        # Regenerate aggregated graphs across all experiment series
        generate_load_capacity_ratio_graph(session, force_direction='y')
        generate_material_thickness_weight_graph(session)
    finally:
        session.close()
