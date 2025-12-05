from database.session import SessionLocal
from graphs.aggregate_graphs import (
    generate_load_capacity_ratio_graph,
    generate_strand_thickness_weight_graph,
    generate_strand_thickness_force_graph,
    generate_strand_thickness_efficiency_graph,
    generate_thickness_height_reduction_vs_force_graph,
    generate_layer_count_height_graph,
    generate_layer_count_force_graph,
    generate_layer_count_efficiency_graph,
    generate_layer_height_reduction_vs_force_graph,
    generate_strand_count_weight_graph,
    generate_strand_count_force_graph,
    generate_strand_count_efficiency_graph,
    generate_strand_height_reduction_vs_force_graph,
    generate_recovery_by_thickness_graph,
    generate_recovery_by_layers_graph,
    generate_recovery_by_strands_graph,
    generate_recovery_heatmap_thickness_layers,
    generate_recovery_heatmap_strands_layers,
    generate_recovery_heatmap_strands_thickness,
    generate_recovery_parameter_importance_graph,
    generate_equilibrium_time_graph
)

if __name__ == '__main__':
    session = SessionLocal()
    try:
        print("Generating aggregate graphs...")

        print("  - Load capacity ratio (y)...")
        generate_load_capacity_ratio_graph(session, force_direction='y')

        print("  - Material thickness vs weight...")
        generate_strand_thickness_weight_graph(session)

        print("  - Material thickness vs force...")
        generate_strand_thickness_force_graph(session)

        print("  - Material thickness vs efficiency...")
        generate_strand_thickness_efficiency_graph(session)

        print("  - Thickness height reduction vs force...")
        generate_thickness_height_reduction_vs_force_graph(session)

        print("  - Layer count vs height...")
        generate_layer_count_height_graph(session)

        print("  - Layer count vs force...")
        generate_layer_count_force_graph(session)

        print("  - Layer count vs efficiency...")
        generate_layer_count_efficiency_graph(session)

        print("  - Layer height reduction vs force...")
        generate_layer_height_reduction_vs_force_graph(session)

        print("  - Strand count vs weight...")
        generate_strand_count_weight_graph(session)

        print("  - Strand count vs force...")
        generate_strand_count_force_graph(session)

        print("  - Strand count vs efficiency...")
        generate_strand_count_efficiency_graph(session)

        print("  - Strand height reduction vs force...")
        generate_strand_height_reduction_vs_force_graph(session)

        print("  - Recovery by thickness...")
        generate_recovery_by_thickness_graph(session)

        print("  - Recovery by layers...")
        generate_recovery_by_layers_graph(session)

        print("  - Recovery by strands...")
        generate_recovery_by_strands_graph(session)

        print("  - Recovery heatmap (thickness × layers)...")
        generate_recovery_heatmap_thickness_layers(session)

        print("  - Recovery heatmap (strands × layers)...")
        generate_recovery_heatmap_strands_layers(session)

        print("  - Recovery heatmap (strands × thickness)...")
        generate_recovery_heatmap_strands_thickness(session)

        print("  - Recovery parameter importance...")
        generate_recovery_parameter_importance_graph(session)

        print("  - Equilibrium time...")
        generate_equilibrium_time_graph(session)

        print("\nAll aggregate graphs generated successfully!")

    finally:
        session.close()
