import os
from multiprocessing import Pool
from experiments.experiment import experiment_loop
from tqdm import tqdm
from database.experiment_series_queries import select_experiment_series_by_name
from database.session import SessionLocal


def run_a_single_experiment(experiment_series_name, experiment_config):  
    session = SessionLocal()
    experiment_series = select_experiment_series_by_name(session, experiment_series_name)
    experiment_loop(experiment_series, experiment_config)
    session.close()


def run_experiments(experiment_series):
    NUM_EXPERIMENTS = experiment_series.num_experiments
    NUM_CONCURRENT_EXPERIMENTS = os.cpu_count()

    experiment_configs = []

    initial_y = experiment_series.initial_force_applied_in_y_direction
    final_y = experiment_series.final_force_in_y_direction
    initial_x = experiment_series.initial_force_applied_in_x_direction
    final_x = experiment_series.final_force_in_x_direction
    initial_z = experiment_series.initial_force_applied_in_z_direction
    final_z = experiment_series.final_force_in_z_direction
    

    for i in range(NUM_EXPERIMENTS):
        config = {
            "experiment_id": i + 1,
            "will_visualize": True,
            "will_record_video": False,
            "torsional_force": experiment_series.torsional_force,
            "max_simulation_time": getattr(experiment_series, 'max_simulation_time', None)
	    }
        
        
        denominator = NUM_EXPERIMENTS - 1 if NUM_EXPERIMENTS > 1 else 1 # Basically to avoid division by zero for the first experiment
        step_ratio = i / denominator
        config["force_in_y_direction"] = initial_y + (final_y - initial_y) * step_ratio
        config["force_in_x_direction"] = initial_x + (final_x - initial_x) * step_ratio
        config["force_in_z_direction"] = initial_z + (final_z - initial_z) * step_ratio


        experiment_configs.append(config)

    with Pool(processes=NUM_CONCURRENT_EXPERIMENTS) as pool:
        results = []
        for experiment_config in experiment_configs:
            result = pool.apply_async(run_a_single_experiment, args=(experiment_series.experiment_series_name, experiment_config))
            results.append(result)
        for result in tqdm(results, desc="Running experiments"):
            result.get()


def run_no_experiment(experiment_series, will_visualize=True, will_record_video=False, run_without_simulation_loop=True):
    """
    This function sets up the experiment series to not run any force applied
    It will be used to take a screenshot and calculate the properties of the structure
    """

    experiment_config = {
        "experiment_id": 1,
        "force_in_y_direction": 0.0,
        "force_in_x_direction": 0.0,
        "force_in_z_direction": 0.0,
        "torsional_force": experiment_series.torsional_force,
        "will_visualize": will_visualize,
        "will_record_video": will_record_video,
        "run_without_simulation_loop": run_without_simulation_loop,
        "max_simulation_time": getattr(experiment_series, 'max_simulation_time', None)
    }

    with Pool(processes=1) as pool:
        pool.apply(run_a_single_experiment, (experiment_series.experiment_series_name, experiment_config))


def run_visual_simulation_experiment(experiment_series, experiment):
    config = {
        "experiment_id": experiment.experiment_id,
        "force_in_y_direction": experiment.force_in_y_direction,
        "force_in_x_direction": experiment.force_in_x_direction,
        "force_in_z_direction": experiment.force_in_z_direction,
        "torsional_force": experiment.torsional_force,
        "will_visualize": True,
        "will_record_video": False,
        "max_simulation_time": float("inf")
    }

    with Pool(processes=1) as pool:
        pool.apply(run_a_single_experiment, (experiment_series.experiment_series_name, config))
