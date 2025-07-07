from dataclasses import dataclass, field
from threading import Lock

@dataclass
class BraidedStructureConfig:
	rebuild_requested: bool = False
	num_strands: int = 5
	radius: float = 0.15
	pitch: float = 1.13
	num_layers: int = 10


