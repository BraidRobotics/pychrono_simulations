from config import BraidedStructureConfig
import pychrono as chrono
from util import take_model_screenshot, take_screenshot, make_video_from_frames

from database.experiment_series_queries import update_experiment_series
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
    layers, node_positions, beam_elements = create_braid_structure(braid_mesh, braid_material, braided_structure_config)


    ####################################################################################################
    # Structural Integrity Checks / Weight Calculation
    ####################################################################################################


    from util import calculate_has_exploded, compute_bounding_box

    initial_bounds = compute_bounding_box(node_positions)

    ####################################################################################################
    # Applying Forces
    ####################################################################################################


    from forces import apply_force_to_all_nodes, apply_force_to_top_nodes, place_box


    # todo apply in x direction too
    apply_force_to_all_nodes(layers, experiment_config["force_in_y_direction"])
    top_nodes = layers[-1]
    # apply_force_to_top_nodes(top_nodes, force_in_y_direction=-2)

    # place_box(top_nodes, system, floor_material)


    ####################################################################################################
    # Visualization
    ####################################################################################################

    from visualization import create_visualization \

    visualization = None
    will_visualize = experiment_series["will_visualize"] or experiment_series.get("run_without_simulation_loop", False)

    if (will_visualize):
        visualization = create_visualization(system, floor, braid_mesh, initial_bounds)


    ####################################################################################################
    # Without Simulation loop
    ####################################################################################################
    from util import calculate_model_weight, calculate_model_height

    if experiment_config.get("run_without_simulation_loop", False):

        while visualization is None or visualization.Run():
            time_step = 0.01

            system.DoStepDynamics(time_step)
            visualization.BeginScene()
            visualization.Render()
            visualization.EndScene()
            system.DoStepDynamics(time_step)
            visualization.BeginScene()
            visualization.Render()

            weight_kg = calculate_model_weight(beam_elements, braid_material)
            height_m = calculate_model_height(beam_elements)

            update_experiment_series(experiment_series["experiment_series_name"], {
                "weight_kg": weight_kg,
                "height_m": height_m,
            })

            take_model_screenshot(visualization, experiment_series["experiment_series_name"])
        
            return


    ####################################################################################################
    # Simulation loop
    ####################################################################################################
    timestep = 0.01

    while visualization is None or visualization.Run():
        
        system.DoStepDynamics(timestep)
        time_passed = system.GetChTime()

        (
            max_bounding_box_volume,
            max_beam_strain,
            max_node_velocity,
            time_to_bounding_box_explosion,
            time_to_beam_strain_exceed_explosion,
            time_to_node_velocity_spike_explosion
        ) = calculate_has_exploded(
            time_passed,
            beam_elements,
            initial_bounds,
            experiment_series
        )

        if experiment_series["will_visualize"]:
            visualization.BeginScene()
            visualization.Render()
            if experiment_series["will_record_video"]:
                take_screenshot(visualization, experiment_series["experiment_series_name"])
            visualization.EndScene()


        if time_passed > experiment_series["max_simulation_time"]:
            insert_experiment(
                experiment_config["experiment_id"],
                experiment_series["experiment_series_name"],
                experiment_config["force_in_y_direction"],
                experiment_config["force_in_x_direction"],
                time_to_bounding_box_explosion,
                max_bounding_box_volume,
                time_to_beam_strain_exceed_explosion,
                max_beam_strain,
                time_to_node_velocity_spike_explosion,
                max_node_velocity
            )

            if experiment_series["will_record_video"]:
                make_video_from_frames(experiment_series["experiment_series_name"])
            
            break
