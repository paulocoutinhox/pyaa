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
	@echo "- test"
	@echo "- test-coverage"
	@echo "- test-coverage-ci"
	@echo ""
	@echo "- docker-build"
	@echo "- docker-rebuild"
	@echo "- docker-run"
	@echo "- docker-run-prod"
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
	DJANGO_SUPERUSER_USERNAME="admin" \
	DJANGO_SUPERUSER_EMAIL="admin@admin.com" \
	DJANGO_SUPERUSER_PASSWORD="admin" \
	python3 manage.py createsuperuser --noinput

run:
	python3 manage.py runserver "0.0.0.0:8000"

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
		-p 8000:8000 pyaa

docker-run-prod:
	@echo "Running..."
	@docker run --rm \
		-v ${PWD}/logs:/app/logs \
		-v ${PWD}/cache:/app/cache \
		-v ${PWD}/db:/app/db \
		-v ${PWD}/media:/app/media \
		-e DJANGO_SETTINGS_MODULE="pyaa.settings.prod" \
		-p 8000:8000 pyaaa
