from sqlalchemy import and_
from sqlalchemy.orm import aliased
from collections import defaultdict

from database.models.experiment_series_model import ExperimentSeries
from database.models.experiment_model import Experiment

from graphs import TARGET_HEIGHT_REDUCTION_PERCENT


def filter_force_no_force_experiments(experiments, initial_height):
	"""
	Filter force_no_force experiments to exclude those after structural compromise.

	Applies filters in order:
	1. Explosion indicators (bounding box, beam strain, node velocity)
	2. Missing required data (height_under_load, final_height)
	3. Monotonic compression check - stops when height_under_load increases
	4. Recovery threshold - stops at very low recovery indicating plastic deformation

	Returns only valid experiments up to the point of structural compromise.
	"""
	if not experiments or not initial_height:
		return []

	# Sort by experiment_id to ensure sequential processing
	sorted_experiments = sorted(experiments, key=lambda e: e.experiment_id)

	valid_experiments = []
	min_height_under_load = float('inf')

	for exp in sorted_experiments:
		# Filter 1: Skip explosions
		if (exp.time_to_bounding_box_explosion is not None or
			exp.time_to_beam_strain_exceed_explosion is not None or
			exp.time_to_node_velocity_spike_explosion is not None):
			continue

		# Filter 2: Skip missing data
		if exp.height_under_load is None or exp.final_height is None:
			continue

		# Filter 3: Check monotonic decrease in height_under_load
		# If height starts increasing, structure is compromised - stop here
		# Use 1% tolerance to account for measurement noise
		if exp.height_under_load > min_height_under_load * 1.01:
			break  # All subsequent experiments are invalid

		# Filter 4: Check height loss indicates structural damage
		# Height loss = final_height - initial_height
		# Positive height loss (final_height > initial_height) indicates structural damage
		height_loss = exp.final_height - initial_height
		if height_loss > 0:
			break  # Material gained height after unloading - structure is damaged

		# Update minimum height and add to valid list
		min_height_under_load = min(min_height_under_load, exp.height_under_load)
		valid_experiments.append(exp)

	return valid_experiments


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
	"""Get strand thickness vs. specific load capacity (structural efficiency)"""
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
	"""Get layer count vs. height for validation"""
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
	"""Get layer count vs. load-bearing capacity"""
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
	"""Get layer count vs. specific load capacity (structural efficiency)"""
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
	"""Get all experiments from layer series for height reduction vs. force graph"""
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
	"""Get all experiments from strand series for height reduction vs. force graph"""
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
	"""Get all experiments from strand thickness series for height reduction vs. force graph"""
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


def get_strand_thickness_max_survivable_force_data(session):
	"""Get maximum force survived before explosion for each strand thickness"""
	thickness_series = session.query(ExperimentSeries).filter(
		ExperimentSeries.group_name.like('%strand_thickness%')
	).all()

	series_map = {s.experiment_series_name: s for s in thickness_series}

	experiments = session.query(Experiment).filter(
		Experiment.experiment_series_name.in_([s.experiment_series_name for s in thickness_series])
	).order_by(
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

		max_force = 0
		max_compression_pct = 0

		for experiment in experiments:
			# Only consider experiments that did NOT explode
			if experiment.time_to_bounding_box_explosion is not None:
				continue

			if experiment.height_under_load is None or experiment.force_in_y_direction is None:
				continue

			force = abs(experiment.force_in_y_direction)
			compression_pct = ((series.height_m - experiment.height_under_load) / series.height_m) * 100

			if force > max_force:
				max_force = force
				max_compression_pct = compression_pct

		results.append({
			"experiment_series_name": series_name,
			"strand_radius": series.strand_radius,
			"max_force_survived": max_force,
			"max_compression_pct": max_compression_pct
		})

	return results


def get_strand_count_vs_weight_chart_values(session):
	"""Get strand count vs. weight for validation"""
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
	"""Get strand count vs. load-bearing capacity"""
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
	"""Get strand count vs. specific load capacity (structural efficiency)"""
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

		# Get all experiments for this series
		all_experiments = session.query(Experiment).filter(
			Experiment.experiment_series_name == series.experiment_series_name
		).all()

		# Apply comprehensive filtering including monotonicity check
		valid_experiments = filter_force_no_force_experiments(all_experiments, series.height_m)

		if not valid_experiments:
			continue

		# Calculate average height loss and final height for this series
		height_losses = []
		final_heights = []
		for exp in valid_experiments:
			height_loss = exp.final_height - series.height_m
			height_losses.append(height_loss)
			final_heights.append(exp.final_height)

		if height_losses:
			avg_height_loss = sum(height_losses) / len(height_losses)
			avg_final_height = sum(final_heights) / len(final_heights)
			results.append({
				"experiment_series_name": series.experiment_series_name,
				"strand_radius": series.strand_radius,
				"num_layers": series.num_layers,
				"num_strands": series.num_strands,
				"recovery_percent": avg_height_loss,
				"avg_final_height": avg_final_height,
				"weight_kg": series.weight_kg
			})

	return results


def get_force_no_force_equilibrium_data(session):
	"""Get equilibrium time data for force_no_force experiments with all parameters"""
	series_list = session.query(ExperimentSeries).filter(
		ExperimentSeries.group_name.like('%force_no_force%')
	).all()

	results = []

	for series in series_list:
		if not series.height_m or not series.reset_force_after_seconds:
			continue

		# Get all experiments for this series
		all_experiments = session.query(Experiment).filter(
			Experiment.experiment_series_name == series.experiment_series_name
		).all()

		# Apply comprehensive filtering including monotonicity check
		valid_experiments = filter_force_no_force_experiments(all_experiments, series.height_m)

		# Further filter for equilibrium data
		experiments_with_equilibrium = [exp for exp in valid_experiments
										if exp.equilibrium_after_seconds is not None]

		if not experiments_with_equilibrium:
			continue

		# Calculate average equilibrium time for this series
		equilibrium_times = [exp.equilibrium_after_seconds for exp in experiments_with_equilibrium]

		if equilibrium_times:
			avg_equilibrium_time = sum(equilibrium_times) / len(equilibrium_times)
			results.append({
				"experiment_series_name": series.experiment_series_name,
				"strand_radius": series.strand_radius,
				"num_layers": series.num_layers,
				"num_strands": series.num_strands,
				"avg_equilibrium_time": avg_equilibrium_time,
				"weight_kg": series.weight_kg
			})

	return results


def get_force_no_force_compression_data(session):
	"""Get compression data for force_no_force experiments"""
	series_list = session.query(ExperimentSeries).filter(
		ExperimentSeries.group_name.like('%force_no_force%')
	).all()

	results = []

	for series in series_list:
		if not series.height_m:
			continue

		# Get all experiments for this series
		all_experiments = session.query(Experiment).filter(
			Experiment.experiment_series_name == series.experiment_series_name
		).all()

		# Apply comprehensive filtering including monotonicity check
		valid_experiments = filter_force_no_force_experiments(all_experiments, series.height_m)

		# Further filter for force data
		experiments_with_force = [exp for exp in valid_experiments
								  if exp.force_in_y_direction is not None]

		if not experiments_with_force:
			continue

		# Calculate compressions
		compressions = []
		for exp in experiments_with_force:
			compression = series.height_m - exp.height_under_load
			if compression > 0:
				compression_pct = (compression / series.height_m) * 100
				compressions.append(compression_pct)

		if compressions:
			avg_compression = sum(compressions) / len(compressions)
			max_compression = max(compressions)
			min_compression = min(compressions)
			results.append({
				"experiment_series_name": series.experiment_series_name,
				"num_layers": series.num_layers,
				"num_strands": series.num_strands,
				"avg_compression_pct": avg_compression,
				"max_compression_pct": max_compression,
				"min_compression_pct": min_compression,
				"target_force": abs(series.final_force_in_y_direction)
			})

	return results


def get_force_no_force_stiffness_data(session):
	"""Get effective stiffness data for force_no_force experiments"""
	series_list = session.query(ExperimentSeries).filter(
		ExperimentSeries.group_name.like('%force_no_force%')
	).all()

	results = []

	for series in series_list:
		if not series.height_m:
			continue

		# Get all experiments for this series
		all_experiments = session.query(Experiment).filter(
			Experiment.experiment_series_name == series.experiment_series_name
		).all()

		# Apply comprehensive filtering including monotonicity check
		valid_experiments = filter_force_no_force_experiments(all_experiments, series.height_m)

		# Further filter for force data
		experiments_with_force = [exp for exp in valid_experiments
								  if exp.force_in_y_direction is not None]

		if not experiments_with_force:
			continue

		# Calculate stiffness k = F/Δx for each experiment
		stiffnesses = []
		for exp in experiments_with_force:
			displacement = series.height_m - exp.height_under_load
			force = abs(exp.force_in_y_direction)
			if displacement > 0 and force > 0:
				stiffness = force / displacement  # N/m
				stiffnesses.append(stiffness)

		if stiffnesses:
			avg_stiffness = sum(stiffnesses) / len(stiffnesses)
			results.append({
				"experiment_series_name": series.experiment_series_name,
				"num_layers": series.num_layers,
				"num_strands": series.num_strands,
				"avg_stiffness": avg_stiffness,
				"weight_kg": series.weight_kg
			})

	return results


def get_force_no_force_recovery_consistency_data(session):
	"""Get recovery data with variance/consistency metrics as compression percentages"""
	series_list = session.query(ExperimentSeries).filter(
		ExperimentSeries.group_name.like('%force_no_force%')
	).all()

	results = []

	for series in series_list:
		if not series.height_m or not series.reset_force_after_seconds:
			continue

		# Get all experiments for this series
		all_experiments = session.query(Experiment).filter(
			Experiment.experiment_series_name == series.experiment_series_name
		).all()

		# Apply comprehensive filtering including monotonicity check
		valid_experiments = filter_force_no_force_experiments(all_experiments, series.height_m)

		if not valid_experiments:
			continue

		# Calculate compression percentages for each experiment
		# Compression % = (initial_height - final_height) / initial_height * 100
		compression_pcts = []
		for exp in valid_experiments:
			compression_pct = ((series.height_m - exp.final_height) / series.height_m) * 100
			compression_pcts.append(compression_pct)

		if len(compression_pcts) >= 2:
			import statistics
			avg_compression_pct = statistics.mean(compression_pcts)
			std_compression_pct = statistics.stdev(compression_pcts)
			min_compression_pct = min(compression_pcts)
			max_compression_pct = max(compression_pcts)

			results.append({
				"experiment_series_name": series.experiment_series_name,
				"num_layers": series.num_layers,
				"num_strands": series.num_strands,
				"initial_height": series.height_m,
				"avg_compression_pct": avg_compression_pct,
				"std_compression_pct": std_compression_pct,
				"min_compression_pct": min_compression_pct,
				"max_compression_pct": max_compression_pct,
				"sample_size": len(compression_pcts)
			})

	return results


def get_strand_count_stiffness_vs_compression_data(session):
	"""Get stiffness vs. compression data for all strand count series"""
	strand_series = session.query(ExperimentSeries).filter(
		ExperimentSeries.group_name.like('%number_of_strands%')
	).all()

	# Include all strand counts
	strand_series = [s for s in strand_series if s.num_strands >= 2]

	series_map = {s.experiment_series_name: s for s in strand_series}

	experiments = session.query(Experiment).filter(
		Experiment.experiment_series_name.in_([s.experiment_series_name for s in strand_series])
	).order_by(
		Experiment.experiment_series_name,
		Experiment.experiment_id
	).all()

	results = []
	for experiment in experiments:
		series = series_map.get(experiment.experiment_series_name)
		if not series or not series.height_m:
			continue

		if experiment.height_under_load is None or experiment.force_in_y_direction is None:
			continue

		# Skip the first experiment (zero force)
		if experiment.experiment_id == 1:
			continue

		displacement = series.height_m - experiment.height_under_load
		if displacement <= 0:
			continue

		compression_pct = (displacement / series.height_m) * 100
		force = abs(experiment.force_in_y_direction)
		stiffness = force / displacement  # k = F/Δx in N/m

		results.append({
			"experiment_series_name": experiment.experiment_series_name,
			"num_strands": series.num_strands,
			"experiment_id": experiment.experiment_id,
			"force": force,
			"displacement": displacement,
			"compression_pct": compression_pct,
			"stiffness": stiffness
		})

	return results


def get_strand_count_force_vs_displacement_data(session):
	"""Get force vs. displacement data for all strand count series"""
	strand_series = session.query(ExperimentSeries).filter(
		ExperimentSeries.group_name.like('%number_of_strands%')
	).all()

	# Include all strand counts
	strand_series = [s for s in strand_series if s.num_strands >= 2]

	series_map = {s.experiment_series_name: s for s in strand_series}

	experiments = session.query(Experiment).filter(
		Experiment.experiment_series_name.in_([s.experiment_series_name for s in strand_series])
	).order_by(
		Experiment.experiment_series_name,
		Experiment.experiment_id
	).all()

	results = []
	for experiment in experiments:
		series = series_map.get(experiment.experiment_series_name)
		if not series or not series.height_m:
			continue

		if experiment.height_under_load is None or experiment.force_in_y_direction is None:
			continue

		displacement = series.height_m - experiment.height_under_load
		force = abs(experiment.force_in_y_direction)
		compression_pct = (displacement / series.height_m) * 100

		results.append({
			"experiment_series_name": experiment.experiment_series_name,
			"num_strands": series.num_strands,
			"experiment_id": experiment.experiment_id,
			"force": force,
			"displacement": displacement,
			"compression_pct": compression_pct
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

def get_models_meeting_target_count(session):
	"""
	Count how many experiment series have at least one experiment that met the target
	(achieved >= 10% height reduction without exploding).

	Returns:
		dict with 'met_target' count and 'total' count
	"""
	from graphs import TARGET_HEIGHT_REDUCTION_PERCENT

	series_map = {
		row.experiment_series_name: row
		for row in session.query(ExperimentSeries).all()
	}

	experiments = session.query(Experiment).all()

	grouped = defaultdict(list)
	for experiment in experiments:
		grouped[experiment.experiment_series_name].append(experiment)

	met_target_count = 0
	total_count = len(series_map)
	target_height_reduction = TARGET_HEIGHT_REDUCTION_PERCENT / 100

	for series_name, experiments in grouped.items():
		series = series_map.get(series_name)
		if not series or not series.height_m:
			continue

		# Check if any experiment in this series met the target
		series_met_target = False
		for experiment in experiments:
			# Skip experiments that exploded
			if experiment.time_to_bounding_box_explosion is not None:
				continue

			# Skip experiments without height data
			if experiment.height_under_load is None:
				continue

			# Calculate height reduction percentage
			height_reduction = (series.height_m - experiment.height_under_load) / series.height_m

			# Check if met target
			if height_reduction >= target_height_reduction:
				series_met_target = True
				break

		if series_met_target:
			met_target_count += 1

	return {
		'met_target': met_target_count,
		'total': total_count,
		'target_percent': TARGET_HEIGHT_REDUCTION_PERCENT
	}


def get_load_bearing_parameter_importance_data(session):
	"""Get load capacity data from force_no_force experiments for parameter importance analysis"""
	# Query force_no_force experiment series where both strands and layers vary
	force_no_force_series = session.query(ExperimentSeries).filter(
		ExperimentSeries.group_name == 'force_no_force'
	).all()

	series_map = {s.experiment_series_name: s for s in force_no_force_series}

	# Query all experiments from these series
	all_experiments = session.query(Experiment).filter(
		Experiment.experiment_series_name.in_([s.experiment_series_name for s in force_no_force_series])
	).all()

	grouped = defaultdict(list)
	for experiment in all_experiments:
		grouped[experiment.experiment_series_name].append(experiment)

	results = []

	for series_name, experiments in grouped.items():
		series = series_map.get(series_name)
		if not series or not series.height_m or not series.weight_kg:
			continue

		# Apply comprehensive filtering including monotonicity check
		valid_experiments = filter_force_no_force_experiments(experiments, series.height_m)

		# Find the maximum force achieved under load (before release)
		max_force = None

		for experiment in valid_experiments:
			if experiment.force_in_y_direction is None:
				continue

			force_value = abs(experiment.force_in_y_direction)

			if max_force is None or force_value > max_force:
				max_force = force_value

		if max_force is not None:
			weight_force = series.weight_kg * 9.81
			specific_load_capacity = max_force / weight_force if weight_force else None

			if specific_load_capacity is not None:
				results.append({
					"experiment_series_name": series_name,
					"num_layers": series.num_layers,
					"num_strands": series.num_strands,
					"specific_load_capacity": specific_load_capacity
				})

	return results