from database.models.experiment_series_model import ExperimentSeries
from database.models.experiment_model import Experiment
from sqlalchemy.exc import SQLAlchemyError

def sqlalchemy_model_to_dict(model):
	if model is None:
		return None
	return {key: value for key, value in model.__dict__.items() if key != "_sa_instance_state"}

def select_all_experiment_series(session):
	experiment_series = session.query(ExperimentSeries).order_by(ExperimentSeries.experiment_series_name).all()
	return experiment_series


def select_all_experiment_series_grouped(session):
	experiment_series = session.query(ExperimentSeries).order_by(ExperimentSeries.group_name, ExperimentSeries.experiment_series_name).all()
	
	grouped_experiment_series = {}
	for series in experiment_series:
		group_name = series.group_name or "Default"
		if group_name not in grouped_experiment_series:
			grouped_experiment_series[group_name] = []
		grouped_experiment_series[group_name].append(series)
	
	return grouped_experiment_series


def select_experiment_series_by_name(session, experiment_series_name):
	experiment_series = session.query(ExperimentSeries).filter_by(experiment_series_name=experiment_series_name).first()
	return experiment_series


def is_experiment_series_name_unique(session, experiment_series_name):
	count = session.query(ExperimentSeries).filter_by(experiment_series_name=experiment_series_name).count()
	return count == 0


def insert_experiment_series(session, experiment_series):
	try:
		# Validate before inserting
		errors = experiment_series.validate() if hasattr(experiment_series, 'validate') else None
		if errors:
			raise ValueError(f"Validation failed: {errors}")

		session.add(experiment_series)
		session.commit()
		return experiment_series
	except SQLAlchemyError:
		session.rollback()
		raise


def insert_experiment_series_default(session, experiment_series_name):
	try:
		instance = ExperimentSeries(experiment_series_name=experiment_series_name)

		# Validate before inserting
		errors = instance.validate() if hasattr(instance, 'validate') else None
		if errors:
			raise ValueError(f"Validation failed: {errors}")

		session.add(instance)
		session.commit()
		return instance
	except SQLAlchemyError:
		session.rollback()
		raise


def update_experiment_series(session, experiment_series_name, updates):
	if not updates:
		return

	experiment_series = session.query(ExperimentSeries).filter_by(experiment_series_name=experiment_series_name).first()
	if not experiment_series:
		return

	for field, value in updates.items():
		column = ExperimentSeries.__table__.columns.get(field)
		if column is not None:
			try:
				py_type = column.type.python_type
				value = py_type(value)
			except (TypeError, ValueError, NotImplementedError):
				pass
		setattr(experiment_series, field, value)

	errors = experiment_series.validate() if hasattr(experiment_series, 'validate') else None
	if errors:
		session.rollback()
		return None, errors

	session.commit()
	return experiment_series, None


def delete_experiment_series(session, experiment_series_name):
	session.query(Experiment).filter_by(experiment_series_name=experiment_series_name).delete()
	session.query(ExperimentSeries).filter_by(experiment_series_name=experiment_series_name).delete()
	session.commit()
