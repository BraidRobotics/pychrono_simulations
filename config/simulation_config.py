from dataclasses import dataclass

@dataclass
class SimulationConfig:
    will_run_server: bool = None
    will_visualize: bool = None
