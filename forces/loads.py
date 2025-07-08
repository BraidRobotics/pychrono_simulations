import pychrono as chrono


def apply_load_to_node(node, load_vector):
	node.SetForce(load_vector)
	return node


def apply_axial_load(nodes, magnitude):
	loads = []
	for node in nodes[-1]:  # Top nodes
		load = apply_load_to_node(node, chrono.ChVector3d(0, magnitude, 0))
		loads.append(load)
	return loads


def apply_lateral_load(nodes, magnitude, direction='x'):
	loads = []
	vec = chrono.ChVector3d(magnitude if direction == 'x' else 0, 0, magnitude if direction == 'z' else 0)
	for node in nodes[-1]:
		load = apply_load_to_node(node, vec)
		loads.append(load)
	return loads


def apply_torsional_load(nodes, magnitude):
	center = chrono.ChVector3d(0, nodes[-1][0].GetPos().y, 0)
	loads = []
	for node in nodes[-1]:
		radius_vector = node.GetPos() - center
		force_direction = radius_vector.Cross(chrono.ChVector3d(0, 1, 0)).GetNormalized()
		load_vector = force_direction * magnitude
		load = apply_load_to_node(node, load_vector)
		loads.append(load)
	return loads

