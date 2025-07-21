import sys
from pathlib import Path
project_root = Path(__file__).resolve().parents[1]
sys.path.append(str(project_root))

from database.session import SessionLocal
from database.models import ExperimentSeries

session = SessionLocal()
if not session.get(ExperimentSeries, "_default"):
	session.add(ExperimentSeries(experiment_series_name="_default", num_experiments=10, max_simulation_time=5.0, final_force_in_y_direction=-0.5,))
	session.commit()
