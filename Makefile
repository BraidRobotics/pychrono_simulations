.PHONY: init_db migrate_db run_all_non_experiments run_all_experiments run_specific_experiments create_experiment_series_interlaces generate_graphs generate_aggregate_graphs generate_model_images

init_db:
	@rm -f database.db
	@alembic -c database/alembic.ini upgrade head
	@python3 database/seed.py

migrate_db:
	@alembic -c database/alembic.ini revision --autogenerate -m "New migration"
	@alembic -c database/alembic.ini upgrade head

run_all_experiments:
	@python -m meta.run_all_experiment_series

run_all_non_experiments:
	@python -m meta.run_all_non_experiments

run_specific_experiments:
	@python -m meta.run_specific_experiment_series_by_name

create_experiment_series_interlaces:
	@python -m meta.create_experiment_series_interlaces

generate_graphs:
	@python -m graphs

generate_aggregate_graphs:
	@python -m meta.generate_aggregate_graphs

generate_all_model_images:
	@python -m meta.generate_all_model_images
