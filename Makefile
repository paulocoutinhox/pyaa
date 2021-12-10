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
	@echo "- migrate"
	@echo "- migration-reset"
	@echo "- create-su"
	@echo ""

format:
	black .

setup:
	pip install -r requirements.txt --upgrade

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
	python manage.py makemigrations
	python manage.py migrate
	@make create-su
	
migrate:
	python manage.py migrate customer 0001
	python manage.py migrate language 0001
	python manage.py makemigrations
	python manage.py migrate
	
create-su:
	DJANGO_SUPERUSER_USERNAME="admin" \
	DJANGO_SUPERUSER_EMAIL="admin@admin.com" \
	DJANGO_SUPERUSER_PASSWORD="admin" \
	python manage.py createsuperuser --noinput
