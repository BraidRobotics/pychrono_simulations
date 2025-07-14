import pychrono as chrono


def apply_axial_force_to_all_nodes(nodes, force_value):
	for layer in nodes:
		for node in layer:
			node.SetForce(chrono.ChVector3d(0, force_value, 0))


def apply_axial_force_to_top_layer(nodes, force_value):
	for node in nodes[-1]:
		node.SetForce(chrono.ChVector3d(0, force_value, 0))



def apply_lateral_load(nodes, magnitude, direction='x'):
	for layer in nodes:
		for node in layer:
			if direction == 'x':
				node.SetForce(chrono.ChVector3d(magnitude, 0, 0))
			elif direction == 'z':
				node.SetForce(chrono.ChVector3d(0, 0, magnitude))


def apply_torsional_load(nodes, magnitude):
	center = chrono.ChVector3d(0, nodes[-1][0].GetPos().y, 0)
	for layer in nodes:
		for node in layer:
			r = node.GetPos() - center
			r_mag = r.Length()
			if r_mag == 0:
				continue
			tangential_direction = r.Cross(chrono.ChVector3d(0, 1, 0)).GetNormalized()
			force = tangential_direction * (magnitude / r_mag)
			node.SetForce(force)
