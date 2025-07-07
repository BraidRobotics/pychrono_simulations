
def calculate_has_exploded(time_passed, beam_elements, initial_bounds, experiment_series):
    if not hasattr(calculate_has_exploded, "_initialized"):
        calculate_has_exploded._max_volume = 0.0
        calculate_has_exploded._max_strain = 0.0
        calculate_has_exploded._max_velocity = 0.0
        calculate_has_exploded._time_to_box = None
        calculate_has_exploded._time_to_strain = None
        calculate_has_exploded._time_to_velocity = None
        calculate_has_exploded._initialized = True

    bounding_box_volume_threshold = experiment_series["bounding_box_volume_threshold"]
    beam_strain_threshold = experiment_series["beam_strain_threshold"]
    node_velocity_threshold = experiment_series["node_velocity_threshold"]

    bounding_box_exploded, volume = check_bounding_box_explosion(beam_elements, initial_bounds, bounding_box_volume_threshold, verbose=True)
    beam_strain_exceeded, strain = check_beam_strain_exceed(beam_elements, beam_strain_threshold, verbose=False)
    velocity_spike_detected, velocity = check_node_velocity_spike(beam_elements, node_velocity_threshold, verbose=False)

    calculate_has_exploded._max_volume = max(calculate_has_exploded._max_volume, volume)
    calculate_has_exploded._max_strain = max(calculate_has_exploded._max_strain, strain)
    calculate_has_exploded._max_velocity = max(calculate_has_exploded._max_velocity, velocity)

    if bounding_box_exploded and not calculate_has_exploded._time_to_box:
        calculate_has_exploded._time_to_box = time_passed

    if beam_strain_exceeded and not calculate_has_exploded._time_to_strain:
        calculate_has_exploded._time_to_strain = time_passed

    if velocity_spike_detected and not calculate_has_exploded._time_to_velocity:
        calculate_has_exploded._time_to_velocity = time_passed

    return (
        calculate_has_exploded._max_volume,
        calculate_has_exploded._max_strain,
        calculate_has_exploded._max_velocity,
        calculate_has_exploded._time_to_box,
        calculate_has_exploded._time_to_strain,
        calculate_has_exploded._time_to_velocity
    )


def get_current_node_positions_from_beam_elements(beam_elements):
	positions = []

	for element in beam_elements:
		positions.append(element.GetNodeA().GetPos())
		positions.append(element.GetNodeB().GetPos())

	return positions


def compute_bounding_box(positions):
	xs = [p.x for p in positions]
	ys = [p.y for p in positions]
	zs = [p.z for p in positions]
	
	return {
		"min_x": min(xs), "max_x": max(xs),
		"min_y": min(ys), "max_y": max(ys),
		"min_z": min(zs), "max_z": max(zs),
	}


def check_bounding_box_explosion(beam_elements, initial_bounds, volume_threshold=2.0, verbose=True):
    current_node_positions = get_current_node_positions_from_beam_elements(beam_elements)
    current_bounds = compute_bounding_box(current_node_positions)

    current_volume = (current_bounds["max_x"] - current_bounds["min_x"]) * \
                     (current_bounds["max_y"] - current_bounds["min_y"]) * \
                     (current_bounds["max_z"] - current_bounds["min_z"])

    initial_volume = (initial_bounds["max_x"] - initial_bounds["min_x"]) * \
                     (initial_bounds["max_y"] - initial_bounds["min_y"]) * \
                     (initial_bounds["max_z"] - initial_bounds["min_z"])

    has_exploded = current_volume > (volume_threshold * initial_volume)

    if has_exploded and verbose:
        print("🛑 Explosion detected: bounding box exceeded threshold")

    return has_exploded, current_volume



def check_beam_strain_exceed(beam_elements, strain_threshold=0.25, verbose=True):
	if not hasattr(check_beam_strain_exceed, "_rest_lengths"):
		check_beam_strain_exceed._rest_lengths = {
			beam: (beam.GetNodeB().GetPos() - beam.GetNodeA().GetPos()).Length()
			for beam in beam_elements
		}

	max_strain = 0.0
	for beam in beam_elements:
		nodeA = beam.GetNodeA().GetPos()
		nodeB = beam.GetNodeB().GetPos()
		current_length = (nodeB - nodeA).Length()
		rest_length = check_beam_strain_exceed._rest_lengths.get(beam, 0)
		if rest_length > 0:
			strain = abs((current_length - rest_length) / rest_length)
			if strain > max_strain:
				max_strain = strain
			if strain > strain_threshold:
				if verbose:
					print(f"🛑 Beam strain exceeded: {strain:.2f} > {strain_threshold:.2f}")
				return True, max_strain
	return False, max_strain


def check_node_velocity_spike(beam_elements, velocity_threshold=10.0, verbose=True):
	if not hasattr(check_node_velocity_spike, "_last_positions"):
		check_node_velocity_spike._last_positions = {}

	spike_detected = False
	max_velocity = 0.0

	for beam in beam_elements:
		for node in [beam.GetNodeA(), beam.GetNodeB()]:
			pos = node.GetPos()
			node_id = id(node)

			last_pos = check_node_velocity_spike._last_positions.get(node_id)
			if last_pos is not None:
				# Estimate velocity as displacement per frame (Δx / Δt)
				vel = (pos - last_pos).Length()  # Assuming timestep is constant
				if vel > max_velocity:
					max_velocity = vel
				if vel > velocity_threshold:
					if verbose:
						print(f"🛑 Velocity spike: {vel:.2f} > {velocity_threshold:.2f}")
					spike_detected = True

			check_node_velocity_spike._last_positions[node_id] = pos

	return spike_detected, max_velocity



