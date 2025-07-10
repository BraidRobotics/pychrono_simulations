import pychrono as chrono
from util import take_model_screenshot, take_screenshot, make_video_from_frames

from database.experiment_series_queries import update_experiment_series
from database.experiments_queries import insert_experiment
from database.session import SessionLocal

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
    
    braid_mesh = create_braid_mesh()
    braid_material = create_braid_material(material_radius = 0.008)
    floor_material = create_floor_material()

    system.Add(braid_mesh)

    from structure import create_floor, create_braid_structure

    floor = create_floor(system, floor_material)
    nodes, node_positions, beam_elements = create_braid_structure(braid_mesh, braid_material, experiment_series)


    ####################################################################################################
    # Structural Integrity Checks / Weight Calculation
    ####################################################################################################


    from util import calculate_has_exploded, compute_bounding_box

    initial_bounds = compute_bounding_box(node_positions)

    ####################################################################################################
    # Applying Forces
    ####################################################################################################


    from forces import apply_axial_load, apply_lateral_load, apply_torsional_load


    ''' These need to be reapplied at every timestep because FEA only supports SetForce which is reset at every timestep
     Quote from the documentation api.projectchrono.org/loads.html: "For FEA nodes, similary to the ChForce for ChBody, 
     it is possible to add a force directly to the node through ChNodeFEAxyz::SetForce(). 
     However, in this case the options are even more limited, since the force is expressed as a simple ChVector3, 
     thus always assumed constant and expressed in absolute frame. The ChNodeFEAxyzrot class implements also ChNodeFEAxyzrot::SetTorque()."
    '''


    ####################################################################################################
    # Visualization
    ####################################################################################################

    from visualization import create_visualization \

    visualization = None
    will_visualize = experiment_config.get("will_visualize", False) or experiment_config.get("run_without_simulation_loop", False)

    if (will_visualize):
        visualization = create_visualization(system, floor, braid_mesh, initial_bounds)


    ####################################################################################################
    # Database session
    ####################################################################################################

    session = SessionLocal()

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

            update_experiment_series(session, experiment_series.experiment_series_name, {
                "weight_kg": weight_kg,
                "height_m": height_m,
            })
            session.close()

            take_model_screenshot(visualization, experiment_series.experiment_series_name)
        
            return


    ####################################################################################################
    # Simulation loop
    ####################################################################################################
    timestep = 0.01

    while visualization is None or visualization.Run():
        # Forces
        apply_axial_load(nodes, experiment_config["force_in_y_direction"])
        apply_lateral_load(nodes, experiment_config["force_in_x_direction"], direction="x")
        apply_lateral_load(nodes, experiment_config["force_in_z_direction"], direction="z")
        apply_torsional_load(nodes, experiment_config["torsional_force"])

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



        if experiment_config.get("will_visualize", False):
            visualization.BeginScene()
            visualization.Render()
            if experiment_config.get("will_record_video", False):
                take_screenshot(visualization, experiment_series.experiment_series_name)
            visualization.EndScene()


        if time_passed > experiment_config["max_simulation_time"]:
            height_m = calculate_model_height(beam_elements)

            insert_experiment(
                session,
                experiment_config["experiment_id"],
                experiment_series.experiment_series_name,
                experiment_config["force_in_y_direction"],
                experiment_config["force_in_x_direction"],
                experiment_config["force_in_z_direction"],
                experiment_config["torsional_force"],
                time_to_bounding_box_explosion,
                max_bounding_box_volume,
                time_to_beam_strain_exceed_explosion,
                max_beam_strain,
                time_to_node_velocity_spike_explosion,
                max_node_velocity,
                height_m
            )
            session.close()

            if experiment_config.get("will_record_video", False):
                make_video_from_frames(experiment_series.experiment_series_name)
            
            break
