ROOT_DIR=${PWD}

.DEFAULT_GOAL := help

# general
help:
	@echo "Type: make [rule]. Available options are:"
	@echo ""
	@echo "- help"
	@echo "- format"
	@echo "- deps"
	@echo "- deps-update"
	@echo "- setup"
	@echo ""
	@echo "- migrate"
	@echo "- migration-reset"
	@echo "- create-su"
	@echo "- fixtures"
	@echo ""
	@echo "- run"
	@echo "- run-worker"
	@echo ""
	@echo "- test"
	@echo "- test-coverage"
	@echo "- test-coverage-ci"
	@echo ""
	@echo "- docker-build"
	@echo "- docker-rebuild"
	@echo "- docker-run"
	@echo "- docker-run-prod"
	@echo ""
	@echo "- docker-cron-build"
	@echo "- docker-cron-run"
	@echo "- docker-cron-run-prod"
	@echo ""

format:
	black .

deps:
	python3 -m pip install -r requirements.txt

deps-update:
	python3 -m pip install pip-check-updates
	pcu -u

setup:
	mkdir -p logs && chmod -R 777 logs
	mkdir -p cache && chmod -R 777 cache
	mkdir -p db && chmod -R 777 db
	mkdir -p static && chmod -R 777 static
	mkdir -p media && chmod -R 777 media

migration-reset:
	find ./apps -type d -name "migrations" -exec rm -rfv {} +
	find . -name "db.sqlite3" -delete

	for app in $(shell find ./apps -mindepth 1 -maxdepth 1 -type d ! -name "__*"); do \
		python3 manage.py makemigrations $$(basename $$app); \
	done

	python3 manage.py migrate
	@make fixtures
	@make create-su

migrate:
	python3 manage.py makemigrations
	python3 manage.py migrate

create-su:
	python3 manage.py createadmin --username admin --email admin@admin.com --password admin --noinput

run:
	python3 manage.py runserver "0.0.0.0:8000"

run-worker:
	python3 manage.py qcluster

fixtures:
	python3 manage.py loaddata initial

test:
	python3 manage.py test

test-coverage:
	coverage run --source='.' manage.py test
	coverage report
	coverage html

test-coverage-ci:
	coverage run --source='.' manage.py test
	coverage report
	coverage xml

docker-build:
	docker build -t pyaa .

docker-rebuild:
	docker build --no-cache -t pyaa .

docker-run:
	@echo "Running..."
	@docker run --rm \
		-v ${PWD}/logs:/app/logs \
		-v ${PWD}/cache:/app/cache \
		-v ${PWD}/db:/app/db \
		-v ${PWD}/media:/app/media \
		-v ${PWD}/static:/app/static \
		-p 8000:8000 pyaa

docker-run-prod:
	@echo "Running..."
	@docker run --rm \
		-v ${PWD}/logs:/app/logs \
		-v ${PWD}/cache:/app/cache \
		-v ${PWD}/db:/app/db \
		-v ${PWD}/media:/app/media \
		-v ${PWD}/static:/app/static \
		-e DJANGO_SETTINGS_MODULE="pyaa.settings.prod" \
		-p 8000:8000 pyaa

docker-cron-build:
	docker build -t pyaa-cron -f Dockerfile.cron .

docker-cron-run:
	@echo "Running..."
	@docker run --rm \
		-v ${PWD}/logs:/app/logs \
		-v ${PWD}/cache:/app/cache \
		-v ${PWD}/db:/app/db \
		-v ${PWD}/media:/app/media \
		-v ${PWD}/static:/app/static \
		pyaa-cron

docker-cron-run-prod:
	@echo "Running..."
	@docker run --rm \
		-v ${PWD}/logs:/app/logs \
		-v ${PWD}/cache:/app/cache \
		-v ${PWD}/db:/app/db \
		-v ${PWD}/media:/app/media \
		-v ${PWD}/static:/app/static \
		-e DJANGO_SETTINGS_MODULE="pyaa.settings.prod" \
		pyaa-cron
