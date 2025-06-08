from dataclasses import dataclass

@dataclass
class SimulationConfig:
    will_run_server: bool = False
    will_visualize: bool = False
    will_take_screenshots: bool = False
    will_record_video: bool = False
