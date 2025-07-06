import os
from multiprocessing import Pool
from config import ExperimentConfig, SimulationConfig
from experiments.experiment import experiment_loop


def run_single_experiment(experiment_config):
    print(f"Running experiment with force_applied {experiment_config.force_applied_in_y_direction}")
    
    simulation_config = SimulationConfig(will_run_server=False, will_visualize=False)

    experiment_loop(simulation_config, experiment_config)


def run_experiments(experiment_series):
    print(f"Running experiments for series:", experiment_series)
    NUM_EXPERIMENTS = experiment_series["num_experiments"]

    NUM_CONCURRENT_EXPERIMENTS = os.cpu_count()
    
    experiment_configs = []
    for i in range(NUM_EXPERIMENTS):

        force_in_y_direction = [i for _ in range(NUM_EXPERIMENTS) for i in range(20, 81)]

        experiment_config = ExperimentConfig(
            experiment_name="Structural Integrity Test",
            description="Test of braided structure under applied forces",
            time_to_explosion=0,
            max_simulation_time=2.5,
            force_applied_in_y_direction=force_in_y_direction[i],
            force_applied_in_x_direction=0.0,
            force_type="TOP_NODES_DOWN",
            meta_data=""
        )
        experiment_configs.append(experiment_config)

    with Pool(processes=NUM_CONCURRENT_EXPERIMENTS) as pool:
        results = []
        for experiment_config in experiment_configs:
            result = pool.apply_async(run_single_experiment, args=(experiment_config,))
            results.append(result)
        for result in results:
            result.wait()


