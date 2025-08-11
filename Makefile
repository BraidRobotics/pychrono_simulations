.PHONY: init_db migrate_db run_all_experiments create_experiment_series_interlaces

init_db:
	@rm -f database.db
	@alembic -c database/alembic.ini upgrade head
	@python3 database/seed.py

migrate_db:
	@alembic -c database/alembic.ini revision --autogenerate -m "New migration"
	@alembic -c database/alembic.ini upgrade head

run_all_experiments:
	@python -m meta.run_all_experiment_series

create_experiment_series_interlaces:
	@python -m meta.create_experiment_series_interlaces
