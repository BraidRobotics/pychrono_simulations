from sqlalchemy import and_
from sqlalchemy.orm import aliased
from collections import defaultdict

from database.models.experiment_series_model import ExperimentSeries
from database.models.experiment_model import Experiment

from graphs import TARGET_HEIGHT_REDUCTION_PERCENT

def get_weight_for_series(session, experiment_series_name):
	series = session.query(ExperimentSeries).filter_by(experiment_series_name=experiment_series_name).first()
	return series.weight_kg if series else None

def get_strand_radius_vs_weight_chart_values(session):
    values = session.query(
        ExperimentSeries.experiment_series_name,
        ExperimentSeries.strand_radius,
        ExperimentSeries.weight_kg
    ).filter(ExperimentSeries.group_name.like('%strand_thickness%')).all()

    return [
        {
            "experiment_series_name": row.experiment_series_name,
            "strand_radius": row.strand_radius,
            "weight_kg": row.weight_kg
        }
        for row in values
    ]


def get_strand_radius_vs_force_chart_values(session):
    series_map = {
        row.experiment_series_name: row
        for row in session.query(ExperimentSeries).filter(ExperimentSeries.group_name.like('%strand_thickness%')).all()
    }

    experiments = session.query(Experiment).order_by(
        Experiment.experiment_series_name,
        Experiment.experiment_id
    ).all()

    grouped = defaultdict(list)
    for experiment in experiments:
        grouped[experiment.experiment_series_name].append(experiment)

    results = []
    target_height_reduction = TARGET_HEIGHT_REDUCTION_PERCENT / 100

    for series_name, experiments in grouped.items():
        series = series_map.get(series_name)
        if not series or not series.height_m or not series.strand_radius:
            continue

        best_experiment = None

        for experiment in experiments:
            if experiment.time_to_bounding_box_explosion is not None:
                continue

            if experiment.height_under_load is None or experiment.force_in_y_direction is None:
                continue

            height_reduction = (series.height_m - experiment.height_under_load) / series.height_m

            if height_reduction >= target_height_reduction:
                if best_experiment is None:
                    best_experiment = experiment
                else:
                    best_height_reduction = (series.height_m - best_experiment.height_under_load) / series.height_m
                    if abs(height_reduction - target_height_reduction) < abs(best_height_reduction - target_height_reduction):
                        best_experiment = experiment

        if best_experiment:
            results.append({
                "experiment_series_name": series_name,
                "strand_radius": series.strand_radius,
                "force": abs(best_experiment.force_in_y_direction)
            })

    return results


def get_strand_radius_vs_efficiency_chart_values(session):
	"""Get strand thickness vs specific load capacity (structural efficiency)"""
	series_map = {
		row.experiment_series_name: row
		for row in session.query(ExperimentSeries).filter(ExperimentSeries.group_name.like('%strand_thickness%')).all()
	}

	experiments = session.query(Experiment).order_by(
		Experiment.experiment_series_name,
		Experiment.experiment_id
	).all()

	grouped = defaultdict(list)
	for experiment in experiments:
		grouped[experiment.experiment_series_name].append(experiment)

	results = []
	target_height_reduction = TARGET_HEIGHT_REDUCTION_PERCENT / 100

	for series_name, experiments in grouped.items():
		series = series_map.get(series_name)
		if not series or not series.height_m or not series.strand_radius or not series.weight_kg:
			continue

		best_experiment = None

		for experiment in experiments:
			if experiment.time_to_bounding_box_explosion is not None:
				continue

			if experiment.height_under_load is None or experiment.force_in_y_direction is None:
				continue

			height_reduction = (series.height_m - experiment.height_under_load) / series.height_m

			if height_reduction >= target_height_reduction:
				if best_experiment is None:
					best_experiment = experiment
				else:
					best_height_reduction = (series.height_m - best_experiment.height_under_load) / series.height_m
					if abs(height_reduction - target_height_reduction) < abs(best_height_reduction - target_height_reduction):
						best_experiment = experiment

		if best_experiment:
			force_value = abs(best_experiment.force_in_y_direction)
			weight_force = series.weight_kg * 9.81
			specific_load_capacity = force_value / weight_force if weight_force else None

			if specific_load_capacity is not None:
				results.append({
					"experiment_series_name": series_name,
					"strand_radius": series.strand_radius,
					"specific_load_capacity": specific_load_capacity
				})

	return results


def get_layer_count_vs_height_chart_values(session):
	"""Get layer count vs height for validation"""
	values = session.query(
		ExperimentSeries.experiment_series_name,
		ExperimentSeries.num_layers,
		ExperimentSeries.height_m
	).filter(
		ExperimentSeries.height_m.isnot(None),
		ExperimentSeries.group_name.like('%number_of_layers%')
	).all()

	return [
		{
			"experiment_series_name": row.experiment_series_name,
			"num_layers": row.num_layers,
			"height_m": row.height_m
		}
		for row in values
	]


def get_layer_count_vs_force_chart_values(session):
	"""Get layer count vs force capacity"""
	series_map = {
		row.experiment_series_name: row
		for row in session.query(ExperimentSeries).filter(ExperimentSeries.group_name.like('%number_of_layers%')).all()
	}

	experiments = session.query(Experiment).order_by(
		Experiment.experiment_series_name,
		Experiment.experiment_id
	).all()

	grouped = defaultdict(list)
	for experiment in experiments:
		grouped[experiment.experiment_series_name].append(experiment)

	results = []
	target_height_reduction = TARGET_HEIGHT_REDUCTION_PERCENT / 100

	for series_name, experiments in grouped.items():
		series = series_map.get(series_name)
		if not series or not series.height_m or not series.num_layers:
			continue

		best_experiment = None

		for experiment in experiments:
			if experiment.time_to_bounding_box_explosion is not None:
				continue

			if experiment.height_under_load is None or experiment.force_in_y_direction is None:
				continue

			height_reduction = (series.height_m - experiment.height_under_load) / series.height_m

			if height_reduction >= target_height_reduction:
				if best_experiment is None:
					best_experiment = experiment
				else:
					best_height_reduction = (series.height_m - best_experiment.height_under_load) / series.height_m
					if abs(height_reduction - target_height_reduction) < abs(best_height_reduction - target_height_reduction):
						best_experiment = experiment

		if best_experiment:
			results.append({
				"experiment_series_name": series_name,
				"num_layers": series.num_layers,
				"force": abs(best_experiment.force_in_y_direction)
			})

	return results


def get_layer_count_vs_efficiency_chart_values(session):
	"""Get layer count vs specific load capacity (structural efficiency)"""
	series_map = {
		row.experiment_series_name: row
		for row in session.query(ExperimentSeries).filter(ExperimentSeries.group_name.like('%number_of_layers%')).all()
	}

	experiments = session.query(Experiment).order_by(
		Experiment.experiment_series_name,
		Experiment.experiment_id
	).all()

	grouped = defaultdict(list)
	for experiment in experiments:
		grouped[experiment.experiment_series_name].append(experiment)

	results = []
	target_height_reduction = TARGET_HEIGHT_REDUCTION_PERCENT / 100

	for series_name, experiments in grouped.items():
		series = series_map.get(series_name)
		if not series or not series.height_m or not series.num_layers or not series.weight_kg:
			continue

		best_experiment = None

		for experiment in experiments:
			if experiment.time_to_bounding_box_explosion is not None:
				continue

			if experiment.height_under_load is None or experiment.force_in_y_direction is None:
				continue

			height_reduction = (series.height_m - experiment.height_under_load) / series.height_m

			if height_reduction >= target_height_reduction:
				if best_experiment is None:
					best_experiment = experiment
				else:
					best_height_reduction = (series.height_m - best_experiment.height_under_load) / series.height_m
					if abs(height_reduction - target_height_reduction) < abs(best_height_reduction - target_height_reduction):
						best_experiment = experiment

		if best_experiment:
			force_value = abs(best_experiment.force_in_y_direction)
			weight_force = series.weight_kg * 9.81
			specific_load_capacity = force_value / weight_force if weight_force else None

			if specific_load_capacity is not None:
				results.append({
					"experiment_series_name": series_name,
					"num_layers": series.num_layers,
					"specific_load_capacity": specific_load_capacity
				})

	return results


def get_layer_height_reduction_vs_force_data(session):
	"""Get all experiments from layer series for height reduction vs force graph"""
	layer_series = session.query(ExperimentSeries).filter(
		ExperimentSeries.group_name.like('%number_of_layers%')
	).all()

	series_map = {s.experiment_series_name: s for s in layer_series}

	experiments = session.query(Experiment).filter(
		Experiment.experiment_series_name.in_([s.experiment_series_name for s in layer_series])
	).all()

	results = []
	for experiment in experiments:
		series = series_map.get(experiment.experiment_series_name)
		if not series or not series.height_m:
			continue

		if experiment.height_under_load is None or experiment.force_in_y_direction is None:
			continue

		height_reduction_pct = ((series.height_m - experiment.height_under_load) / series.height_m) * 100

		results.append({
			"experiment_series_name": experiment.experiment_series_name,
			"num_layers": series.num_layers,
			"force": abs(experiment.force_in_y_direction),
			"height_reduction_pct": height_reduction_pct,
			"exploded": experiment.time_to_bounding_box_explosion is not None
		})

	return results


def get_strand_height_reduction_vs_force_data(session):
	"""Get all experiments from strand series for height reduction vs force graph"""
	strand_series = session.query(ExperimentSeries).filter(
		ExperimentSeries.group_name.like('%number_of_strands%')
	).all()

	series_map = {s.experiment_series_name: s for s in strand_series}

	experiments = session.query(Experiment).filter(
		Experiment.experiment_series_name.in_([s.experiment_series_name for s in strand_series])
	).all()

	results = []
	for experiment in experiments:
		series = series_map.get(experiment.experiment_series_name)
		if not series or not series.height_m:
			continue

		if experiment.height_under_load is None or experiment.force_in_y_direction is None:
			continue

		height_reduction_pct = ((series.height_m - experiment.height_under_load) / series.height_m) * 100

		results.append({
			"experiment_series_name": experiment.experiment_series_name,
			"num_strands": series.num_strands,
			"num_layers": series.num_layers,
			"force": abs(experiment.force_in_y_direction),
			"height_reduction_pct": height_reduction_pct,
			"exploded": experiment.time_to_bounding_box_explosion is not None
		})

	return results


def get_thickness_height_reduction_vs_force_data(session):
	"""Get all experiments from strand thickness series for height reduction vs force graph"""
	thickness_series = session.query(ExperimentSeries).filter(
		ExperimentSeries.group_name.like('%strand_thickness%')
	).all()

	series_map = {s.experiment_series_name: s for s in thickness_series}

	experiments = session.query(Experiment).filter(
		Experiment.experiment_series_name.in_([s.experiment_series_name for s in thickness_series])
	).all()

	results = []
	for experiment in experiments:
		series = series_map.get(experiment.experiment_series_name)
		if not series or not series.height_m:
			continue

		if experiment.height_under_load is None or experiment.force_in_y_direction is None:
			continue

		height_reduction_pct = ((series.height_m - experiment.height_under_load) / series.height_m) * 100

		results.append({
			"experiment_series_name": experiment.experiment_series_name,
			"strand_radius": series.strand_radius,
			"force": abs(experiment.force_in_y_direction),
			"height_reduction_pct": height_reduction_pct,
			"exploded": experiment.time_to_bounding_box_explosion is not None
		})

	return results


def get_strand_count_vs_weight_chart_values(session):
	"""Get strand count vs weight for validation"""
	values = session.query(
		ExperimentSeries.experiment_series_name,
		ExperimentSeries.num_strands,
		ExperimentSeries.weight_kg
	).filter(ExperimentSeries.group_name.like('%number_of_strands%')).all()

	return [
		{
			"experiment_series_name": row.experiment_series_name,
			"num_strands": row.num_strands,
			"weight_kg": row.weight_kg
		}
		for row in values
	]


def get_strand_count_vs_force_chart_values(session):
	"""Get strand count vs force capacity"""
	series_map = {
		row.experiment_series_name: row
		for row in session.query(ExperimentSeries).filter(ExperimentSeries.group_name.like('%number_of_strands%')).all()
	}

	experiments = session.query(Experiment).order_by(
		Experiment.experiment_series_name,
		Experiment.experiment_id
	).all()

	grouped = defaultdict(list)
	for experiment in experiments:
		grouped[experiment.experiment_series_name].append(experiment)

	results = []
	target_height_reduction = TARGET_HEIGHT_REDUCTION_PERCENT / 100

	for series_name, experiments in grouped.items():
		series = series_map.get(series_name)
		if not series or not series.height_m or not series.num_strands:
			continue

		best_experiment = None

		for experiment in experiments:
			if experiment.time_to_bounding_box_explosion is not None:
				continue

			if experiment.height_under_load is None or experiment.force_in_y_direction is None:
				continue

			height_reduction = (series.height_m - experiment.height_under_load) / series.height_m

			if height_reduction >= target_height_reduction:
				if best_experiment is None:
					best_experiment = experiment
				else:
					best_height_reduction = (series.height_m - best_experiment.height_under_load) / series.height_m
					if abs(height_reduction - target_height_reduction) < abs(best_height_reduction - target_height_reduction):
						best_experiment = experiment

		if best_experiment:
			results.append({
				"experiment_series_name": series_name,
				"num_strands": series.num_strands,
				"force": abs(best_experiment.force_in_y_direction)
			})

	return results


def get_strand_count_vs_efficiency_chart_values(session):
	"""Get strand count vs specific load capacity (structural efficiency)"""
	series_map = {
		row.experiment_series_name: row
		for row in session.query(ExperimentSeries).filter(ExperimentSeries.group_name.like('%number_of_strands%')).all()
	}

	experiments = session.query(Experiment).order_by(
		Experiment.experiment_series_name,
		Experiment.experiment_id
	).all()

	grouped = defaultdict(list)
	for experiment in experiments:
		grouped[experiment.experiment_series_name].append(experiment)

	results = []
	target_height_reduction = TARGET_HEIGHT_REDUCTION_PERCENT / 100

	for series_name, experiments in grouped.items():
		series = series_map.get(series_name)
		if not series or not series.height_m or not series.num_strands or not series.weight_kg:
			continue

		best_experiment = None

		for experiment in experiments:
			if experiment.time_to_bounding_box_explosion is not None:
				continue

			if experiment.height_under_load is None or experiment.force_in_y_direction is None:
				continue

			height_reduction = (series.height_m - experiment.height_under_load) / series.height_m

			if height_reduction >= target_height_reduction:
				if best_experiment is None:
					best_experiment = experiment
				else:
					best_height_reduction = (series.height_m - best_experiment.height_under_load) / series.height_m
					if abs(height_reduction - target_height_reduction) < abs(best_height_reduction - target_height_reduction):
						best_experiment = experiment

		if best_experiment:
			force_value = abs(best_experiment.force_in_y_direction)
			weight_force = series.weight_kg * 9.81
			specific_load_capacity = force_value / weight_force if weight_force else None

			if specific_load_capacity is not None:
				results.append({
					"experiment_series_name": series_name,
					"num_strands": series.num_strands,
					"specific_load_capacity": specific_load_capacity
				})

	return results


def get_force_no_force_recovery_data(session):
	"""Get elastic recovery data for force_no_force experiments with all parameters"""
	series_list = session.query(ExperimentSeries).filter(
		ExperimentSeries.group_name.like('%force_no_force%')
	).all()

	results = []

	for series in series_list:
		if not series.height_m or not series.reset_force_after_seconds:
			continue

		experiments = session.query(Experiment).filter(
			Experiment.experiment_series_name == series.experiment_series_name,
			Experiment.time_to_bounding_box_explosion.is_(None),
			Experiment.height_under_load.isnot(None),
			Experiment.final_height.isnot(None)
		).all()

		if not experiments:
			continue

		# Calculate average recovery for this series
		recovery_percentages = []
		for exp in experiments:
			compression = series.height_m - exp.height_under_load
			if compression > 0:  # Avoid division by zero
				recovery = (exp.final_height - exp.height_under_load) / compression * 100
				recovery_percentages.append(recovery)

		if recovery_percentages:
			avg_recovery = sum(recovery_percentages) / len(recovery_percentages)
			results.append({
				"experiment_series_name": series.experiment_series_name,
				"strand_radius": series.strand_radius,
				"num_layers": series.num_layers,
				"num_strands": series.num_strands,
				"recovery_percent": avg_recovery,
				"weight_kg": series.weight_kg
			})

	return results


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
	from graphs import TARGET_HEIGHT_REDUCTION_PERCENT

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

		# Find experiment with target height reduction that didn't explode
		best_experiment = None
		target_height_reduction = TARGET_HEIGHT_REDUCTION_PERCENT / 100

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

			# Select experiment closest to target height reduction
			if height_reduction >= target_height_reduction:
				if best_experiment is None:
					best_experiment = experiment
				else:
					# Compare which is closer to target
					best_height_reduction = (series.height_m - best_experiment.height_under_load) / series.height_m
					if abs(height_reduction - target_height_reduction) < abs(best_height_reduction - target_height_reduction):
						best_experiment = experiment

		if best_experiment:
			force_value = getattr(best_experiment, force_column)
			# Specific Load Capacity = Force / (Weight × g)
			# This gives how many times its own weight the structure can support
			weight_force = series.weight_kg * 9.81  # Convert kg to Newtons
			ratio = abs(force_value) / weight_force if weight_force else None
			if ratio is not None:
				results.append({
					"experiment_series_name": series_name,
					"force": abs(force_value),
					"specific_load_capacity": ratio
				})

	return [dict(r) for r in results]