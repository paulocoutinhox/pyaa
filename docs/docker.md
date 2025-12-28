# Docker

This project includes production-ready Dockerfiles for both synchronous (uWSGI) and asynchronous (Gunicorn + Uvicorn) deployments.

## Available Dockerfiles

- **Dockerfile.web** - Synchronous server using uWSGI (WSGI)
- **Dockerfile.async.web** - Asynchronous server using Gunicorn + Uvicorn workers (ASGI) - **Recommended for production**

You need to set up the project files before using Docker with the following command:

```
make setup
```

## Synchronous Deployment (uWSGI)

Configure Docker with the following commands:

```
make docker-build
make docker-run
```

or:

```
make docker-build
make docker-run-prod
```

Finally, set up the fixtures and create the Super User:

```
docker exec -it pyaa make fixtures
docker exec -it pyaa make create-su
```

## Asynchronous Deployment (Gunicorn + Uvicorn) - **Recommended**

The async version provides better performance and is recommended for production use:

```
make docker-build-async
make docker-run-async-prod
```

Finally, set up the fixtures and create the Super User:

```
docker exec -it pyaa-async make fixtures
docker exec -it pyaa-async make create-su
```

For development:

```
make docker-build-async
make docker-run-async
```

## Docker Volumes

By default, this project uses an SQLite database, which is stored in the db folder that is created automatically.

Additionally, file uploads are stored in the media folder, which is also created automatically.

You need to pass your volume paths to Docker. For example:

```
docker build --no-cache -t pyaa .

docker run --rm \
    -v ${PWD}/logs:/app/logs \
    -v ${PWD}/cache:/app/cache \
    -v ${PWD}/db:/app/db \
    -v ${PWD}/media:/app/media \
    -v ${PWD}/static:/app/static \
    -p 8000:8000 pyaa
```

## Docker Compose

You can use this configuration with Docker Compose (using async version - recommended):

```yml
services:
  nginx:
    image: nginx:latest
    volumes:
      - ./pyaa/nginx.conf:/etc/nginx/conf.d/pyaa.conf
    ports:
      - "80:80"

  pyaa:
    build:
      context: pyaa
      dockerfile: Dockerfile.async.web
    restart: always
    depends_on:
      - mysql
    environment:
      - DJANGO_SETTINGS_MODULE=pyaa.settings.prod
      - APP_ALLOWED_HOSTS=your-domain.com
      - APP_CSRF_TRUSTED_ORIGINS=https://your-domain.com
    volumes:
      - ./pyaa/logs:/app/logs
      - ./pyaa/cache:/app/cache
      - ./pyaa/db:/app/db
      - ./pyaa/media:/app/media
      - ./pyaa/static:/app/static

  pyaa-worker:
    build:
      context: pyaa
      dockerfile: Dockerfile.async.web
    restart: always
    depends_on:
      - pyaa
    environment:
      - DJANGO_SETTINGS_MODULE=pyaa.settings.prod
      - APP_ALLOWED_HOSTS=your-domain.com
      - APP_CSRF_TRUSTED_ORIGINS=https://your-domain.com
    volumes:
      - ./pyaa/logs:/app/logs
      - ./pyaa/cache:/app/cache
      - ./pyaa/db:/app/db
      - ./pyaa/media:/app/media
      - ./pyaa/static:/app/static
    command: /app/worker-entrypoint.sh

  pyaa-cron:
    build:
      context: pyaa
      dockerfile: Dockerfile.cron
    restart: always
    depends_on:
      - pyaa
    environment:
      - DJANGO_SETTINGS_MODULE=pyaa.settings.prod
      - APP_ALLOWED_HOSTS=your-domain.com
      - APP_CSRF_TRUSTED_ORIGINS=https://your-domain.com
    volumes:
      - ./pyaa/logs:/app/logs
      - ./pyaa/cache:/app/cache
      - ./pyaa/db:/app/db
      - ./pyaa/media:/app/media
      - ./pyaa/static:/app/static

  mysql:
    image: mysql:8.4.0
    restart: always
    ports:
      - "3306:3306"
    environment:
      - MYSQL_ROOT_PASSWORD=your-password
    volumes:
      - ./mysql-data:/var/lib/mysql
```

**Note:** For synchronous deployment, replace `Dockerfile.async.web` with `Dockerfile.web` in the configuration above.
