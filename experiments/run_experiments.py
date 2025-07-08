import os
from multiprocessing import Pool
from config import SimulationConfig
from experiments.experiment import experiment_loop
from tqdm import tqdm


def run_a_single_experiment(experiment_series, experiment_config):  
    experiment_loop(experiment_series, experiment_config)


def run_experiments(experiment_series):
    NUM_EXPERIMENTS = experiment_series["num_experiments"]
    NUM_CONCURRENT_EXPERIMENTS = os.cpu_count()

    experiment_series["will_visualize"] = False
    experiment_series["will_record_video"] = False

    experiment_configs = []

    initial_y = experiment_series["initial_force_applied_in_y_direction"]
    final_y = experiment_series["final_force_in_y_direction"]
    initial_x = experiment_series["initial_force_applied_in_x_direction"]
    final_x = experiment_series["final_force_in_x_direction"]

    for i in range(NUM_EXPERIMENTS):
        config = {
            "experiment_id": i + 1,
            "force_in_y_direction": 0.0,
            "force_in_x_direction": 0.0
	    }
        
        # incrementing the force for each experiment starting from initial up to final
        if experiment_series["force_type"] in ("TOP_NODES_DOWN", "ALL_NODES_DOWN"):
            config["force_in_y_direction"] = initial_y + (final_y - initial_y) * (i / (NUM_EXPERIMENTS - 1))
        elif experiment_series["force_type"] == "RIGHT_SIDE_SIDEWAYS":
            config["force_in_x_direction"] = initial_x + (final_x - initial_x) * (i / (NUM_EXPERIMENTS - 1))


        experiment_configs.append(config)

    with Pool(processes=NUM_CONCURRENT_EXPERIMENTS) as pool:
        results = []
        for experiment_config in experiment_configs:
            result = pool.apply_async(run_a_single_experiment, args=(experiment_series, experiment_config))
            results.append(result)
        for result in tqdm(results, desc="Running experiments"):
            result.get()


def run_no_experiment(experiment_series, will_visualize=True, will_record_video=False, run_without_simulation_loop=True):
    """
    This function sets up the experiment series to not run any force applied
    It will be used to take a screenshot and calculate the properties of the structure
    """

    experiment_series["will_visualize"] = will_visualize
    experiment_series["will_record_video"] = will_record_video

    experiment_config = {
        "experiment_id": 1,
        "force_in_y_direction": 0.0,
        "force_in_x_direction": 0.0,
        "run_without_simulation_loop": run_without_simulation_loop
    }

    with Pool(processes=1) as pool:
        pool.apply(run_a_single_experiment, (experiment_series, experiment_config))



if __name__ == "__main__":
    # todo this should be removed eventually, of course
    from database.experiment_series_queries import select_experiment_series_by_name
    experiment_series = select_experiment_series_by_name('_default')

    experiment_series["max_simulation_time"] = 1000
    experiment_series["will_visualize"] = True
    experiment_series["will_record_video"] = False

    experiment_config = {
        "experiment_id": 1,
        "force_in_y_direction": 0.0,
        "force_in_x_direction": 0.0,
        "force_in_z_direction": 0.0,
        "torsional_force": 0.0,
    }
    run_a_single_experiment(experiment_series, experiment_config)
    # run_experiments(experiment_series)
