from .graph_constants import TARGET_HEIGHT_REDUCTION_PERCENT
from .aggregate_graphs import (
    generate_load_capacity_ratio_graph,
    generate_material_thickness_weight_graph,
    generate_material_thickness_force_graph
)
from .series_graphs import (
    generate_experiment_series_force_graph,
    generate_experiment_series_height_graph,
    generate_experiment_series_elastic_recovery_graph
)
from .generate_after_experiments import generate_graphs_after_experiments
