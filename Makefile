ROOT_DIR=${PWD}

.DEFAULT_GOAL := help

# general
help:
	@echo "Type: make [rule]. Available options are:"
	@echo ""
	@echo "- help"
	@echo "- format"
	@echo "- setup"
	@echo ""
	@echo "- migrate"
	@echo "- migration-reset"
	@echo "- create-su"
	@echo ""
	@echo "- run"
	@echo ""
	@echo "- docker-build"
	@echo "- docker-run"
	@echo "- docker-run-prod"
	@echo ""

format:
	black .

setup:
	python3 -m pip install -r requirements.txt --upgrade
	mkdir -p db
	mkdir -p static

migration-reset:
	find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
	find . -path "*/migrations/*.pyc" -delete
	find . -name "db.sqlite3" -delete
	python3 manage.py makemigrations
	python3 manage.py migrate
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

docker-build:
	docker build --no-cache -t pyaa .

docker-run:
	@echo "Running..."
	@docker run --rm -v ${PWD}/db:/app/db \
		-v ${PWD}/media:/app/media \
		-e APP_ENV=dev \
		-e DJANGO_SUPERUSER_USERNAME="admin" \
		-e DJANGO_SUPERUSER_EMAIL="admin@admin.com" \
		-e DJANGO_SUPERUSER_PASSWORD="admin" \
		-p 8000:8000 pyaa

docker-run-prod:
	@echo "Running..."
	@docker run --rm -v ${PWD}/db:/app/db \
		-v ${PWD}/media:/app/media \
		-e APP_ENV=prod \
		-e APP_ALLOWED_HOSTS="localhost" \
		-e APP_CSRF_TRUSTED_ORIGINS="http://localhost" \
		-e DJANGO_SUPERUSER_USERNAME="admin" \
		-e DJANGO_SUPERUSER_EMAIL="admin@admin.com" \
		-e DJANGO_SUPERUSER_PASSWORD="admin" \
		-p 8000:8000 pyaa

tailwind:
	npx tailwindcss -i ./app/static/tailwind/styles.css -o ./static/tailwind/styles.css
