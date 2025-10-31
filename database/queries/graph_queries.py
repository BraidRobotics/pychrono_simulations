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
	for experiment in experiments:
		grouped[experiment.experiment_series_name].append(experiment)

	results = []

	for series_name, experiments in grouped.items():
		series = series_map.get(series_name)
		if not series or not series.height_m:
			continue

		# Find experiment with ~10% height reduction that didn't explode
		best_experiment = None
		target_height_reduction = 0.10  # 10%

		for experiment in experiments:
			# Skip experiments that exploded
			if experiment.time_to_bounding_box_explosion is not None:
				continue

			# Skip experiments without height data
			if experiment.height_under_load is None:
				continue

			force_value = getattr(experiment, force_column)
			if force_value is None:
				continue

			# Calculate height reduction percentage
			height_reduction = (series.height_m - experiment.height_under_load) / series.height_m

			# Select experiment closest to 10% height reduction
			if height_reduction >= target_height_reduction:
				if best_experiment is None:
					best_experiment = experiment
				else:
					# Compare which is closer to 10% target
					best_height_reduction = (series.height_m - best_experiment.height_under_load) / series.height_m
					if abs(height_reduction - target_height_reduction) < abs(best_height_reduction - target_height_reduction):
						best_experiment = experiment

		if best_experiment:
			force_value = getattr(best_experiment, force_column)
			ratio = abs(force_value) / series.weight_kg if series.weight_kg else None
			if ratio is not None:
				results.append({
					"experiment_series_name": series_name,
					"force": force_value,
					"load_capacity_ratio": ratio
				})

	return [dict(r) for r in results]