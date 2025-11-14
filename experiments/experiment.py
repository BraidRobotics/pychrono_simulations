import pychrono as chrono

from config import ExperimentConfig

from util import  take_model_screenshot, take_final_screenshot, take_video_screenshot, make_video_from_frames, reset_structural_integrity_state

from database.queries.experiment_series_queries import update_experiment_series
from database.queries.experiments_queries import insert_experiment
from database.session import SessionLocal

def experiment_loop(experiment_series, experiment_config: ExperimentConfig):

    ####################################################################################################
    # Physics Engine
    ####################################################################################################

    from physics_model import create_braid_mesh, create_strand_material, create_tape_material, create_floor_material
    from os_specifics import setup_solver

    system = chrono.ChSystemSMC()
    system.SetCollisionSystemType(chrono.ChCollisionSystem.Type_BULLET)
    system.SetGravitationalAcceleration(chrono.ChVector3d(0, -9.81, 0))  # gravity

    linear_solver = setup_solver(system)

    ####################################################################################################
    # Mesh / Material
    ####################################################################################################
    
    braid_mesh = create_braid_mesh()
    strand_material = create_strand_material(experiment_series.material_youngs_modulus, experiment_series.material_thickness)
    tape_material = create_tape_material()
    floor_material = create_floor_material()

    system.Add(braid_mesh)

    from structure import create_floor, create_braid_structure

    floor = create_floor(system, floor_material)
    nodes, node_positions, beam_elements = create_braid_structure(braid_mesh, strand_material, tape_material, experiment_series)



    ####################################################################################################
    # Structural Integrity Checks / Weight Calculation
    ####################################################################################################


    from util import calculate_has_exploded, compute_bounding_box

    initial_bounds = compute_bounding_box(node_positions)

    ####################################################################################################
    # Visualization
    ####################################################################################################

    from visualization import create_visualization \

    visualization = None
    will_visualize = experiment_config.will_visualize or experiment_config.is_non_experiment_run

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

    if experiment_config.is_non_experiment_run:

        while visualization is None or visualization.Run():
            time_step = 0.01

            system.DoStepDynamics(time_step)
            visualization.BeginScene()
            visualization.Render()
            visualization.EndScene()
            system.DoStepDynamics(time_step)
            visualization.BeginScene()
            visualization.Render()

            weight_kg = calculate_model_weight(beam_elements, strand_material)
            height_m = calculate_model_height(beam_elements)

            update_experiment_series(session, experiment_series.experiment_series_name, {
                "weight_kg": weight_kg,
                "height_m": height_m,
            })
            session.close()

            take_model_screenshot(visualization, experiment_series.experiment_series_name)
        
            return

    ####################################################################################################
    # Applying Forces
    ####################################################################################################

    # api.projectchrono.org/loads.html

    from forces import apply_loads, reset_loads, is_in_equilibrium, reset_equilibrium_state

    # Reset all stateful function states for this experiment
    reset_equilibrium_state()
    reset_structural_integrity_state()
    
    apply_loads(nodes, experiment_config)


    ####################################################################################################
    # Simulation loop
    ####################################################################################################
    timestep = 0.01
    
    equilibrium_after_seconds = None
    height_under_load = None

    while visualization is None or visualization.Run():
        system.DoStepDynamics(timestep)
        time_passed = system.GetChTime()
        
        if (experiment_series.reset_force_after_seconds is not None) and (time_passed > experiment_series.reset_force_after_seconds):
            if height_under_load is None:
                height_under_load = calculate_model_height(beam_elements)
            reset_loads(nodes)


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

        structure_is_in_equilibrium = is_in_equilibrium(max_beam_strain, max_node_velocity)

        if structure_is_in_equilibrium and equilibrium_after_seconds is None:
            equilibrium_after_seconds = time_passed
            if height_under_load is None:
                height_under_load = calculate_model_height(beam_elements)

        if experiment_config.will_visualize:
            visualization.BeginScene()
            visualization.Render()
            if experiment_config.will_record_video:
                take_video_screenshot(visualization, experiment_series.experiment_series_name)
            visualization.EndScene()

        structure_exploded = time_to_bounding_box_explosion is not None
        reset_done = (experiment_series.reset_force_after_seconds is None) or (time_passed > experiment_series.reset_force_after_seconds)
        times_up = time_passed > experiment_config.max_simulation_time


        if not experiment_config.run_forever and ((structure_is_in_equilibrium and reset_done) or structure_exploded or times_up):

            final_height = calculate_model_height(beam_elements)

            if height_under_load is None and experiment_series.reset_force_after_seconds is None:
                height_under_load = final_height

            if structure_exploded:
                final_height = None
                height_under_load = None
                # Done in order to take a screenshot of the explosion so that it's easier to discern visually that it has exploded
                for _ in range(100):
                    system.DoStepDynamics(timestep)
                    visualization.BeginScene()
                    visualization.Render()
                    visualization.EndScene()
            

            take_final_screenshot(visualization, experiment_series.experiment_series_name, experiment_config.experiment_id)

            insert_experiment(
                session,
                experiment_config.experiment_id,
                experiment_series.experiment_series_name,
                experiment_config.force_in_y_direction,
                experiment_config.force_top_nodes_in_y_direction,
                experiment_config.force_in_x_direction,
                experiment_config.force_in_z_direction,
                experiment_config.torsional_force,
                equilibrium_after_seconds,
                time_to_bounding_box_explosion,
                max_bounding_box_volume,
                time_to_beam_strain_exceed_explosion,
                max_beam_strain,
                time_to_node_velocity_spike_explosion,
                max_node_velocity,
                height_under_load,
                final_height
            )
            session.close()

            if experiment_config.will_record_video:
                make_video_from_frames(experiment_series.experiment_series_name)

            if visualization is not None:
                device = visualization.GetDevice()
                device.closeDevice()
                device.drop()

            break

