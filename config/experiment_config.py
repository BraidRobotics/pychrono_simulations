from dataclasses import dataclass

@dataclass
class ExperimentConfig:
    experiment_name: str = "default_experiment"
    description: str = ""

    time_to_explosion: float = 0.0
    max_simulation_time: float = 10.0
    
    force_applied_in_y_direction: float = 0.0
    force_applied_in_x_direction: float = 0.0

    meta_data: str = ""