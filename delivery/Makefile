PYTHON=/usr/local/bin/python3
PYTEST_PROC_NUM?=4

.DEFAULT: help
.PHONY: migrate, lint, isort, test, makemigrations, migr

help:
	@echo " help    - show help info"
	@echo " migrate - init database and apply migrations"
	@echo " lint    - inspect project source code for errors"
	@echo " isort   - sort imports according to project conventions"
	@echo " test    - run project tests"

migrate:
	sudo -u postgres psql -c "CREATE USER delivery WITH ENCRYPTED PASSWORD 'delivery';" || true
	sudo -u postgres psql -c "ALTER USER delivery CREATEDB;" || true
	sudo -u postgres psql -c "CREATE DATABASE delivery;" || true

	cd migrations && aerich upgrade

lint:
	$(PYTHON) -m flake8 .

isort:
	$(PYTHON) -m isort .

test:
	sudo docker-compose exec api bash -c 'make test'

makemigrations:
	# Запуск: make makemigrations name = <name_of_migtration>
	sudo docker-compose exec api bash -c 'cd api/migrations; aerich migrate --name "$(name)"'

upgradedb:
	sudo docker-compose exec api bash -c 'cd api/migrations; aerich upgrade'