from sqlalchemy import Column, Float, Integer, String, Boolean, DateTime, ForeignKey
from database.models.base import Base

class ExperimentSeries(Base):
	__tablename__ = 'experiment_series'

	experiment_series_name = Column(String, primary_key=True, unique=True, nullable=False)
	description = Column(String, default='')

	# Simulation configuration
	num_experiments = Column(Integer, default=50)
	max_simulation_time = Column(Float, default=10.0)

	# Has Exploded Thresholds
	bounding_box_volume_threshold = Column(Float, default=1.8)
	beam_strain_threshold = Column(Float, default=0.08)
	node_velocity_threshold = Column(Float, default=3.0)

	# Force configurations (initial is the force applied to the first experiment in the series, final is the last)
	# the exact force applied to the experiment is in the experiments table
	initial_force_applied_in_y_direction = Column(Float, default=0.0)
	final_force_in_y_direction = Column(Float, default=0.0)
	initial_top_nodes_force_in_y_direction = Column(Float, default=0.0)
	final_top_nodes_force_in_y_direction = Column(Float, default=0.0)
	initial_force_applied_in_x_direction = Column(Float, default=0.0)
	final_force_in_x_direction = Column(Float, default=0.0)
	initial_force_applied_in_z_direction = Column(Float, default=0.0)
	final_force_in_z_direction = Column(Float, default=0.0)
	torsional_force = Column(Float, default=0.0)
	reset_force_after_seconds = Column(Integer)

	# Braided structure configuration
	num_strands = Column(Integer, default=8)
	num_layers = Column(Integer, default=5)
	radius = Column(Float, default=0.1)
	pitch = Column(Float, default=0.1)  # The distance between two consecutive strands in the same layer
	radius_taper = Column(Float, default=0.0)  # Conicity (how much it narrows towards the top)
	material_thickness = Column(Float, default=0.005)
	material_youngs_modulus = Column(Float, default=1.72e10)  # Glass-reinforced polyester (GRP) https://en.wikipedia.org/wiki/Young%27s_modulus
	weight_kg = Column(Float, default=None)
	height_m = Column(Float, default=None)

	# Meta
	is_experiments_outdated = Column(Boolean, default=False) # Used to know that the values in this table have been changed without rerunning the experiments

	def validate(self):
		errors = []
		if self.num_layers < 2:
			errors.append("Number of layers must be at least 2.")
		if self.num_strands < 2:
			errors.append("Number of strands must be at least 2.")
		if self.radius <= 0:
			errors.append("Radius must be greater than 0.")
		if self.pitch <= 0:
			errors.append("Pitch must be greater than 0.")
		if self.radius_taper * self.num_layers > self.radius:
			errors.append("Radius taper times number of layers must not exceed radius.")
		if self.num_strands % 2 != 0:
			errors.append("Number of strands should be divisible by 2 for symmetry.")
		if self.material_thickness <= 0:
			errors.append("Material thickness must be greater than 0.")
		if self.material_youngs_modulus <= 0:
			errors.append("Material Young's modulus must be greater than 0.")
		return errors