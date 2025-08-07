.PHONY: init_db migrate_db run_all_experiments

init_db:
	@rm -f database.db
	@alembic -c database/alembic.ini upgrade head
	@python3 database/seed.py

migrate_db:
	@alembic -c database/alembic.ini revision --autogenerate -m "New migration"
	@alembic -c database/alembic.ini upgrade head

run_all_experiments:
	@python3 -m meta.run_all_experiment_series