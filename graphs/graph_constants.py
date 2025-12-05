"""
Target height reduction percentage for load capacity analysis.
Used to:
- Find the force required on a strand of a certain thickness to achieve this compression level
      (get_strand_radius_vs_force_chart_values)
- Draw reference lines on height reduction graphs
     (generate_experiment_series_height_graph)
- Calculate load capacity in the aggregated load capacity ratio graph
      (_get_load_capacity_ratio_chart_values)
"""
TARGET_HEIGHT_REDUCTION_PERCENT = 10.0
