from config.experiment_config import ExperimentConfig
import pychrono as chrono
from config import braided_structure_config
from visualization import make_video_from_frames

from database.experiments_queries import insert_experiment

def experiment_loop(simulation_config, experiment_config):

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

    braid_mesh = create_braid_mesh()
    braid_material = create_braid_material(material_radius = 0.008)
    floor_material = create_floor_material()

    system.Add(braid_mesh)

    from structure import create_floor, create_braid_structure, move_braid_structure

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

    apply_force_to_all_nodes(layers, experiment_config.force_applied_in_y_direction)
    # apply_force_to_top_nodes(top_nodes, force_in_y_direction=-2)

    # place_box(top_nodes, system, floor_material)

    ####################################################################################################
    # Server GUI to control simulation parameters
    ####################################################################################################

    from experiments_server.start_server import start_server

    if (simulation_config.will_run_server):
        start_server()


    ####################################################################################################
    # Visualization
    ####################################################################################################

    from visualization import create_visualization \

    visualization = None

    if (simulation_config.will_visualize):
        visualization = create_visualization(system, floor, braid_mesh, initial_bounds)


    ####################################################################################################
    # Simulation loop
    ####################################################################################################
    timestep = 0.01

    try:
        while not simulation_config.will_visualize or visualization.Run():

            system.DoStepDynamics(timestep)

            time_passed = system.GetChTime()

            if simulation_config.will_run_server:
                snapshot = braided_structure_config.get_snapshot()
                if snapshot["rebuild_requested"]:
                    braided_structure_config.update(rebuild_requested=False)
                    move_braid_structure(layers)
                    layers, top_nodes, node_positions, beam_elements = create_braid_structure(braid_mesh, braid_material, braided_structure_config)


            if simulation_config.will_visualize:
                visualization.BeginScene()
                visualization.Render()
                if simulation_config.will_take_screenshots:
                    visualization.TakeScreenshot()
                visualization.EndScene()


            # todo uncomment again later
            # did_bounding_box_explode = check_bounding_box_explosion(beam_elements, initial_bounds, volume_threshold=2.0)
            # did_beam_strain_exceed = check_beam_strain_exceed(beam_elements, strain_threshold=0.25)
            # did_node_velocity_spike = check_node_velocity_spike(beam_elements, velocity_threshold=10.0)
 
            # if did_bounding_box_explode or did_beam_strain_exceed or did_node_velocity_spike:
            #     config_data = experiment_config.__dict__.copy()
            #     config_data["time_to_explosion"] = system.GetChTime()
            #     insert_experiment(**config_data)
            #     break



            if time_passed > experiment_config.max_simulation_time:
                config_data = experiment_config.__dict__.copy()
                insert_experiment(**config_data)
                break


    except KeyboardInterrupt:
        if simulation_config.will_record_video:
            make_video_from_frames()



	