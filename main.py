import pychrono as chrono

##################################################
# Physics Engine
##################################################

from physics_model import create_braid_mesh, create_braid_material, create_floor_material
from os_specifics import setup_solver

system = chrono.ChSystemSMC()
system.SetCollisionSystemType(chrono.ChCollisionSystem.Type_BULLET)
system.SetGravitationalAcceleration(chrono.ChVector3d(0, -9.81, 0))  # gravity

linear_solver = setup_solver(system)

##################################################
# Mesh / Material
##################################################

braid_mesh = create_braid_mesh()
braid_material = create_braid_material(material_radius = 0.008)
floor_material = create_floor_material()

system.Add(braid_mesh)

from structure import create_floor, create_braid_structure

floor = create_floor(system, floor_material)
layers, top_nodes, node_positions, beam_elements = create_braid_structure(braid_mesh, braid_material)


##################################################
# Structural Integrity Checks / Weight Calculation
##################################################


from util import get_current_node_positions_from_beam_elements, compute_bounding_box, check_bounding_box_explosion, \
			check_beam_strain_exceed, check_node_velocity_spike, calculate_model_weight

# calculate_model_weight(beam_elements, braid_material)

initial_bounds = compute_bounding_box(node_positions)

##################################################
# Applying Forces
##################################################


from forces import apply_force_to_all_nodes, apply_force_to_top_nodes, place_box

# apply_force_to_all_nodes(layers, force_in_y_direction=-1)
# apply_force_to_top_nodes(top_nodes, force_in_y_direction=-2)

# place_box(top_nodes, system, floor_material)

##################################################
# Visualization
##################################################

from visualization import create_visualization, output_image_frame

will_visualize = True
visualization = None

if (will_visualize):
    visualization = create_visualization(system, floor, braid_mesh, initial_bounds)

##################################################
# Simulation loop
##################################################

timestep = 0.01

while not will_visualize or visualization.Run():

    system.DoStepDynamics(timestep)

    # check_bounding_box_explosion(beam_elements, initial_bounds, volume_threshold=2.0)

    # check_beam_strain_exceed(beam_elements, strain_threshold=0.25)

    # check_node_velocity_spike(beam_elements, velocity_threshold=10.0)

    if will_visualize:
        visualization.BeginScene()
        visualization.Render()
        # output_image_frame(visualization)
        visualization.EndScene()
