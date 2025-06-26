import pychrono.fea as fea
import pychrono as chrono

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

    return has_exploded



def check_beam_strain_exceed(beam_elements, strain_threshold=0.25, verbose=True):
	if not hasattr(check_beam_strain_exceed, "_rest_lengths"):
		check_beam_strain_exceed._rest_lengths = {
			beam: (beam.GetNodeB().GetPos() - beam.GetNodeA().GetPos()).Length()
			for beam in beam_elements
		}

	for beam in beam_elements:
		nodeA = beam.GetNodeA().GetPos()
		nodeB = beam.GetNodeB().GetPos()
		current_length = (nodeB - nodeA).Length()
		rest_length = check_beam_strain_exceed._rest_lengths.get(beam, 0)
		if rest_length > 0:
			strain = abs((current_length - rest_length) / rest_length)
			if strain > strain_threshold:
				if verbose:
					print(f"🛑 Beam strain exceeded: {strain:.2f} > {strain_threshold:.2f}")
				return True
	return False


def check_node_velocity_spike(beam_elements, velocity_threshold=10.0, verbose=True):
	if not hasattr(check_node_velocity_spike, "_last_positions"):
		check_node_velocity_spike._last_positions = {}

	spike_detected = False

	for beam in beam_elements:
		for node in [beam.GetNodeA(), beam.GetNodeB()]:
			pos = node.GetPos()
			node_id = id(node)

			last_pos = check_node_velocity_spike._last_positions.get(node_id)
			if last_pos is not None:
				# Estimate velocity as displacement per frame (Δx / Δt)
				vel = (pos - last_pos).Length()  # Assuming timestep is constant
				if vel > velocity_threshold:
					if verbose:
						print(f"🛑 Velocity spike: {vel:.2f} > {velocity_threshold:.2f}")
					spike_detected = True

			check_node_velocity_spike._last_positions[node_id] = pos

	return spike_detected

