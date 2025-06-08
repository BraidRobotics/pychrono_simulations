from multiprocessing import Pool
from config import ExperimentConfig, SimulationConfig
from main import main

NUM_EXPERIMENTS = 100 
NUM_CONCURRENT_EXPERIMENTS = 5

def run_single_experiment(experiment_config):
    print(f"Running experiment with force_applied {experiment_config.force_applied}")
    
    simulation_config = SimulationConfig(will_run_server=False, will_visualize=False)

    main(simulation_config, experiment_config)

if __name__ == "__main__":
    experiment_configs = []
    for i in range(NUM_EXPERIMENTS):
        experiment_config = ExperimentConfig(
            experiment_name="Structural Integrity Test",
            description="Test of braided structure under applied forces",
            time_to_explosion=0,
            force_applied=i,
            force_type="TOP_NODES_DOWN",
            braided_structure_config={},
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