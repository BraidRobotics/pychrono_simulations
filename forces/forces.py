import pychrono as chrono

def apply_force_to_all_nodes(layers, force_in_y_direction=-0.2):
	for layer in layers:
		for node in layer:
			node.SetForce(chrono.ChVector3d(0, force_in_y_direction, 0))


# The force is in SI units, so -0.2 = 0.2 N
def apply_force_to_top_nodes(top_nodes, force_in_y_direction=-0.2):
    if force_in_y_direction > 0:
        raise ValueError("Force in y direction must be negative to apply downward force.")
    for node in top_nodes:
        # force in x, y and z direction
        node.SetForce(chrono.ChVector3d(0, force_in_y_direction, 0))


def place_box(top_nodes, system, surface_material):
    # Compute top Y position from top nodes
    node_positions_y = [node.GetPos().y for node in top_nodes]
    highest_node_y = max(node_positions_y)

    # Define box dimensions and properties
    box_width = 0.4
    box_depth = 0.4
    box_height = 0.2
    box_density = 2700  # kg/m³ (aluminum-like)
    box_collision = True
    box_visualization = True

    # Define gap between box and structure
    clearance_gap = 0.01  # 1 cm

    # Create box and position it slightly above top nodes
    box = chrono.ChBodyEasyBox(box_width, box_height, box_depth, box_density, box_collision, box_visualization, surface_material)

    box_center_y = highest_node_y + (box_height / 2.0) + clearance_gap
    box_position = chrono.ChVector3d(0, box_center_y, 0)
    box.SetPos(box_position)


    # Add to simulation
    system.Add(box)
