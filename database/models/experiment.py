from sqlalchemy import Column, Float, Integer, String, Boolean, DateTime, ForeignKey
from database.models.base import Base
from datetime import datetime

class Experiment(Base):
	__tablename__ = 'experiments'

	id = Column(Integer, primary_key=True, autoincrement=True)

	# The experiment_id is not auto-incremented to allow me to set it manually and sort by id later
	# since the experiments are parallelized, they end up saved out of order otherwise.
	experiment_id = Column(Integer, primary_key=False, autoincrement=False)

	experiment_series_name = Column(String, ForeignKey('experiment_series.experiment_series_name'), nullable=False)
	timestamp = Column(DateTime, default=datetime.utcnow)

	# Force applied
	force_in_x_direction = Column(Float)
	force_in_y_direction = Column(Float)
	force_in_z_direction = Column(Float)
	torsional_force = Column(Float)

	# Has Exploded
	time_to_bounding_box_explosion = Column(Float)
	max_bounding_box_volume = Column(Float)
	time_to_beam_strain_exceed_explosion = Column(Float)
	max_beam_strain = Column(Float)
	time_to_node_velocity_spike_explosion = Column(Float)
	max_node_velocity = Column(Float)

	# Final Result
	final_height = Column(Float)