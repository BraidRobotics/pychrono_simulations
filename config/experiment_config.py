from dataclasses import dataclass

@dataclass
class ExperimentConfig:
    experiment_name: str = "default_experiment"
    description: str = ""
    time_to_explosion: float = 0.0
    force_applied: float = 0.0
    force_type: str = ""
    braided_structure_config: dict = None
    meta_data: str = ""