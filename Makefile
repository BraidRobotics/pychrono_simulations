.PHONY: init_db

init_db:
	@rm -f database.db
	@alembic -c database/alembic.ini upgrade head
	@python3 database/seed.py
