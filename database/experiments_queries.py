from sqlalchemy.exc import SQLAlchemyError
from database.models.experiment import Experiment


def select_experiment_by_id(session, experiment_id):
	experiment = session.query(Experiment).filter_by(experiment_id=experiment_id).first()
	return experiment


def select_all_experiments_by_series_name(session, experiment_series_name):
	experiments = session.query(Experiment).filter_by(experiment_series_name=experiment_series_name).order_by(Experiment.experiment_id).all()
	return experiments


def insert_experiment(
	session,
	experiment_id,
	experiment_series_name,
	force_in_y_direction,
	force_in_x_direction,
	force_in_z_direction,
	torsional_force,
	time_to_bounding_box_explosion,
	max_bounding_box_volume,
	time_to_beam_strain_exceed_explosion,
	max_beam_strain,
	time_to_node_velocity_spike_explosion,
	max_node_velocity,
	final_height
):
	try:
		experiment = Experiment(
			experiment_id=experiment_id,
			experiment_series_name=experiment_series_name,
			force_in_y_direction=force_in_y_direction,
			force_in_x_direction=force_in_x_direction,
			force_in_z_direction=force_in_z_direction,
			torsional_force=torsional_force,
			time_to_bounding_box_explosion=time_to_bounding_box_explosion,
			max_bounding_box_volume=max_bounding_box_volume,
			time_to_beam_strain_exceed_explosion=time_to_beam_strain_exceed_explosion,
			max_beam_strain=max_beam_strain,
			time_to_node_velocity_spike_explosion=time_to_node_velocity_spike_explosion,
			max_node_velocity=max_node_velocity,
			final_height=final_height
		)
		session.add(experiment)
		session.commit()
		return experiment
	except SQLAlchemyError:
		session.rollback()
		raise


def delete_experiments_by_series_name(session, experiment_series_name):
	session.query(Experiment).filter_by(experiment_series_name=experiment_series_name).delete()
	session.commit()
