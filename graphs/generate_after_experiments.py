from pathlib import Path
import traceback

from database.queries.experiments_queries import select_all_experiments_by_series_name
from database.session import SessionLocal
from .aggregate_graphs import (
    generate_load_capacity_ratio_graph,
    generate_material_thickness_weight_graph,
    generate_material_thickness_force_graph,
    generate_material_thickness_efficiency_graph,
    generate_layer_count_height_graph,
    generate_layer_count_force_graph,
    generate_layer_count_efficiency_graph,
    generate_strand_count_weight_graph,
    generate_strand_count_force_graph,
    generate_strand_count_efficiency_graph,
    generate_recovery_by_thickness_graph,
    generate_recovery_by_layers_graph,
    generate_recovery_by_strands_graph,
    generate_recovery_heatmap_thickness_layers,
    generate_recovery_parameter_importance_graph
)
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
        generate_experiment_series_elastic_recovery_graph(session, safe_name, experiments, experiment_series.reset_force_after_seconds)

        generate_load_capacity_ratio_graph(session, force_direction='y')
        generate_material_thickness_weight_graph(session)
        generate_material_thickness_force_graph(session)
        generate_material_thickness_efficiency_graph(session)
        generate_layer_count_height_graph(session)
        generate_layer_count_force_graph(session)
        generate_layer_count_efficiency_graph(session)
        generate_strand_count_weight_graph(session)
        generate_strand_count_force_graph(session)
        generate_strand_count_efficiency_graph(session)
        generate_recovery_by_thickness_graph(session)
        generate_recovery_by_layers_graph(session)
        generate_recovery_by_strands_graph(session)
        generate_recovery_heatmap_thickness_layers(session)
        generate_recovery_parameter_importance_graph(session)
    finally:
        session.close()


def delete_relevant_graphs(safe_name):
    graphs_dir = Path(__file__).parent.parent / "experiments_server" / "assets" / "graphs"

    if graphs_dir.exists():
        (graphs_dir / f"series_{safe_name}_force.html").unlink(missing_ok=True)
        (graphs_dir / f"series_{safe_name}_height.html").unlink(missing_ok=True)
        (graphs_dir / f"series_{safe_name}_elastic_recovery.html").unlink(missing_ok=True)
        (graphs_dir / "load_capacity_ratio_y.html").unlink(missing_ok=True)
        (graphs_dir / "material_thickness_vs_weight.html").unlink(missing_ok=True)
        (graphs_dir / "material_thickness_vs_force.html").unlink(missing_ok=True)
        (graphs_dir / "material_thickness_vs_efficiency.html").unlink(missing_ok=True)
        (graphs_dir / "layer_count_vs_height.html").unlink(missing_ok=True)
        (graphs_dir / "layer_count_vs_force.html").unlink(missing_ok=True)
        (graphs_dir / "layer_count_vs_efficiency.html").unlink(missing_ok=True)
        (graphs_dir / "strand_count_vs_weight.html").unlink(missing_ok=True)
        (graphs_dir / "strand_count_vs_force.html").unlink(missing_ok=True)
        (graphs_dir / "strand_count_vs_efficiency.html").unlink(missing_ok=True)
        (graphs_dir / "recovery_by_thickness.html").unlink(missing_ok=True)
        (graphs_dir / "recovery_by_layers.html").unlink(missing_ok=True)
        (graphs_dir / "recovery_by_strands.html").unlink(missing_ok=True)
        (graphs_dir / "recovery_heatmap_thickness_layers.html").unlink(missing_ok=True)
        (graphs_dir / "recovery_parameter_importance.html").unlink(missing_ok=True)
    else:
        graphs_dir.mkdir(parents=True, exist_ok=True)