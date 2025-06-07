from dataclasses import dataclass, field
from threading import Lock

@dataclass
class BraidedStructureConfig:
	rebuild_requested: bool = False
	num_strands: int = 5
	radius: float = 0.15
	pitch: float = 1.13
	num_layers: int = 10
	lock: Lock = field(default_factory=Lock)

	def update(self, **kwargs):
		with self.lock:
			for key, value in kwargs.items():
				if hasattr(self, key):
					setattr(self, key, value)

	def get_snapshot(self):
		with self.lock:
			return {
				"rebuild_requested": self.rebuild_requested,
				"num_strands": self.num_strands,
				"radius": self.radius,
				"pitch": self.pitch,
				"num_layers": self.num_layers
			}
	

braided_structure_config = BraidedStructureConfig()