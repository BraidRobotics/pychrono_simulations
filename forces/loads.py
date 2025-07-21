import pychrono as chrono


def apply_loads(nodes, experiment_config):
	force_y = experiment_config.get("force_in_y_direction", 0.0)
	force_top_y = experiment_config.get("force_top_nodes_in_y_direction", 0.0)
	force_x = experiment_config.get("force_in_x_direction", 0.0)
	force_z = experiment_config.get("force_in_z_direction", 0.0)
	torsional = experiment_config.get("torsional_force", 0.0)

	for layer_index, layer in enumerate(nodes):
		for node in layer:
			force = chrono.ChVector3d(0, 0, 0)

			# Y force for all nodes
			force += chrono.ChVector3d(0, force_y, 0)

			# Lateral force
			force += chrono.ChVector3d(force_x, 0, force_z)

			# Torsional force
			center = chrono.ChVector3d(0, nodes[-1][0].GetPos().y, 0)
			r = node.GetPos() - center
			r_mag = r.Length()
			if r_mag != 0:
				tangential_direction = r.Cross(chrono.ChVector3d(0, 1, 0)).GetNormalized()
				force += tangential_direction * (torsional / r_mag)

			# Add extra force to top layer
			if layer_index == len(nodes) - 1:
				force += chrono.ChVector3d(0, force_top_y, 0)

			node.SetForce(force)


def reset_loads(nodes):
	for layer in nodes:
		for node in layer:
			node.SetForce(chrono.ChVector3d(0, 0, 0))
			node.SetTorque(chrono.ChVector3d(0, 0, 0))
