from sqlalchemy import and_
from sqlalchemy.orm import aliased
from collections import defaultdict

from database.models.experiment_series_model import ExperimentSeries
from database.models.experiment_model import Experiment

def get_material_thickness_vs_weight_chart_values(session):
    values = session.query(
        ExperimentSeries.experiment_series_name,
        ExperimentSeries.material_thickness,
        ExperimentSeries.weight_kg
    ).all()

    return [
        {
            "experiment_series_name": row.experiment_series_name,
            "material_thickness": row.material_thickness,
            "weight_kg": row.weight_kg
        }
        for row in values
    ]


def get_load_capacity_ratio_y_chart_values(session):
	return _get_load_capacity_ratio_chart_values(session, "force_in_y_direction")

def get_load_capacity_ratio_x_chart_values(session):
	return _get_load_capacity_ratio_chart_values(session, "force_in_x_direction")

def get_load_capacity_ratio_z_chart_values(session):
	return _get_load_capacity_ratio_chart_values(session, "force_in_z_direction")

def get_load_capacity_ratio_top_nodes_chart_values(session):
	return _get_load_capacity_ratio_chart_values(session, "force_top_nodes_in_y_direction")

def get_load_capacity_ratio_torsional_chart_values(session):
	return _get_load_capacity_ratio_chart_values(session, "torsional_force")


def _get_load_capacity_ratio_chart_values(session, force_column):

	series_map = {
		row.experiment_series_name: row
		for row in session.query(ExperimentSeries).all()
	}

	experiments = session.query(Experiment).order_by(
		Experiment.experiment_series_name,
		Experiment.experiment_id
	).all()

	grouped = defaultdict(list)
	for exp in experiments:
		grouped[exp.experiment_series_name].append(exp)

	results = []

	for series_name, exps in grouped.items():
		series = series_map.get(series_name)
		if not series:
			continue

		exploded_idx = next((i for i, e in enumerate(exps) if e.time_to_bounding_box_explosion is not None), None)
		if exploded_idx is None or exploded_idx == 0:
			continue

		for prev_idx in reversed(range(exploded_idx)):
			exp = exps[prev_idx]
			force_value = getattr(exp, force_column)
			if exp.time_to_bounding_box_explosion is None and force_value is not None:
				ratio = abs(force_value) / series.weight_kg if series.weight_kg else None
				if ratio is not None:
					results.append({
						"experiment_series_name": series_name,
						"force": force_value,
						"load_capacity_ratio": ratio
					})
				break

	return results