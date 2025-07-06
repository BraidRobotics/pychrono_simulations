from config import BraidedStructureConfig
import pychrono as chrono
from visualization import make_video_from_frames

from database.experiments_queries import insert_experiment

def experiment_loop(experiment_series, experiment_config):

    ####################################################################################################
    # Physics Engine
    ####################################################################################################

    from physics_model import create_braid_mesh, create_braid_material, create_floor_material
    from os_specifics import setup_solver

    system = chrono.ChSystemSMC()
    system.SetCollisionSystemType(chrono.ChCollisionSystem.Type_BULLET)
    system.SetGravitationalAcceleration(chrono.ChVector3d(0, -9.81, 0))  # gravity

    linear_solver = setup_solver(system)

    ####################################################################################################
    # Mesh / Material
    ####################################################################################################
    
    # todo make sure that this is correct
    braided_structure_config = BraidedStructureConfig(
        num_strands=experiment_series["num_strands"],
        num_layers=experiment_series["num_layers"],
        radius=experiment_series["radius"],
        pitch=experiment_series["pitch"]
    )

    braid_mesh = create_braid_mesh()
    braid_material = create_braid_material(material_radius = 0.008)
    floor_material = create_floor_material()

    system.Add(braid_mesh)

    from structure import create_floor, create_braid_structure

    floor = create_floor(system, floor_material)
    layers, top_nodes, node_positions, beam_elements = create_braid_structure(braid_mesh, braid_material, braided_structure_config)


    ####################################################################################################
    # Structural Integrity Checks / Weight Calculation
    ####################################################################################################


    from util import get_current_node_positions_from_beam_elements, compute_bounding_box, check_bounding_box_explosion, \
                check_beam_strain_exceed, check_node_velocity_spike, calculate_model_weight

    # calculate_model_weight(beam_elements, braid_material)

    initial_bounds = compute_bounding_box(node_positions)

    ####################################################################################################
    # Applying Forces
    ####################################################################################################


    from forces import apply_force_to_all_nodes, apply_force_to_top_nodes, place_box

    # todo apply in x direction too
    apply_force_to_all_nodes(layers, experiment_config["force_in_y_direction"])
    # apply_force_to_top_nodes(top_nodes, force_in_y_direction=-2)

    # place_box(top_nodes, system, floor_material)


    ####################################################################################################
    # Visualization
    ####################################################################################################

    from visualization import create_visualization \

    visualization = None

    if (experiment_series["will_visualize"]):
        visualization = create_visualization(system, floor, braid_mesh, initial_bounds)


    ####################################################################################################
    # Simulation loop
    ####################################################################################################
    timestep = 0.01


    while not experiment_series["will_visualize"] or visualization.Run():

        system.DoStepDynamics(timestep)

        time_passed = system.GetChTime()

        if experiment_series["will_visualize"]:
            visualization.BeginScene()
            visualization.Render()
            if experiment_series["will_take_screenshots"]:
                visualization.TakeScreenshot()
            visualization.EndScene()


        did_bounding_box_explode = check_bounding_box_explosion(beam_elements, initial_bounds, volume_threshold=2.0)
        did_beam_strain_exceed = check_beam_strain_exceed(beam_elements, strain_threshold=0.25)
        did_node_velocity_spike = check_node_velocity_spike(beam_elements, velocity_threshold=10.0)



        if time_passed > experiment_series["max_simulation_time"]:
            insert_experiment(
                experiment_series_id = experiment_series["id"],
                force_in_y_direction = experiment_config["force_in_y_direction"],
                force_in_x_direction = experiment_config["force_in_x_direction"],
                time_to_bounding_box_explosion = None,
                time_to_beam_strain_exceed_explosion = None,
                time_to_node_velocity_spike_explosion = None,
            )

            if experiment_series["will_record_video"]:
                make_video_from_frames()
            
            break


