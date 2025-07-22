from dataclasses import dataclass
from warnings import warn

@dataclass
class ExperimentConfig:
	experiment_id: int
	max_simulation_time: float

	force_in_y_direction: float = 0.0
	force_top_nodes_in_y_direction: float = 0.0
	force_in_x_direction: float = 0.0
	force_in_z_direction: float = 0.0
	torsional_force: float = 0.0

	is_non_experiment_run: bool = False
	will_visualize: bool = False
	will_record_video: bool = False


	def __post_init__(self):
		if self.force_in_y_direction > 0:
			warn("⚠️: force_in_y_direction is positive which means that it puts upwards against gravity. Are you sure? ⚠️")

