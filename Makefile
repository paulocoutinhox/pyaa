ROOT_DIR=${PWD}

.DEFAULT_GOAL := help

# general
help:
	@echo "Type: make [rule]. Available options are:"
	@echo ""
	@echo "- help"
	@echo "- format"
	@echo "- setup"
	@echo "- backup"
	@echo "- restore-backup"
	@echo ""
	@echo "- migrate"
	@echo "- migration-reset"
	@echo "- create-su"
	@echo ""
	@echo "- run"
	@echo "- run-gunicorn"
	@echo ""
	@echo "- docker-build"
	@echo "- docker-run"
	@echo ""

format:
	black .

setup:
	python3 -m pip install -r requirements.txt --upgrade

backup:
	cd ../ && \
	tar -zcvf ~/Dropbox/Public/pyaa.tar.gz pyaa

restore-backup:
	cd ../ && \
	mv pyaa pyaa-$(shell date +'%y%m%d-%H%M%S') && \
	mkdir pyaa && \
	tar -xvf ~/Dropbox/Public/pyaa.tar.gz -C .

migration-reset:
	find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
	find . -path "*/migrations/*.pyc" -delete
	find . -name "db.sqlite3" -delete
	python3 manage.py makemigrations
	python3 manage.py migrate
	@make create-su

migrate:
	python3 manage.py migrate customer 0001
	python3 manage.py migrate language 0001
	python3 manage.py makemigrations
	python3 manage.py migrate

create-su:
	DJANGO_SUPERUSER_USERNAME="admin" \
	DJANGO_SUPERUSER_EMAIL="admin@admin.com" \
	DJANGO_SUPERUSER_PASSWORD="admin" \
	python3 manage.py createsuperuser --noinput

run:
	python3 manage.py runserver

run-gunicorn:
	gunicorn --bind 0.0.0.0:8000 main.wsgi

docker-build:
	docker build --no-cache -t pyaa .

docker-run:
	@echo "Running..."
	@docker run --rm -p 8000:8000 pyaa
