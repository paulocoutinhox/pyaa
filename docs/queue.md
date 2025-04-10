# Queue

This project uses django-q2 for task queuing and processing. Below are instructions for running and managing the queue workers.

## Running Queue Workers Locally

To run a queue worker locally, use the following command:

```
make run-worker
```

or

```
python3 manage.py qcluster
```

## Running Queue Workers with Docker

### Building the Docker Image

First, build the Docker image:

```
docker build -t pyaa .
```

or

```
docker build -t pyaa .
```

### Running the Worker with Docker

To run the worker in Docker, override the default entrypoint command:

```
docker run --rm \
    -v ${PWD}/logs:/app/logs \
    -v ${PWD}/cache:/app/cache \
    -v ${PWD}/db:/app/db \
    -v ${PWD}/media:/app/media \
    -v ${PWD}/static:/app/static \
    pyaa python3 manage.py qcluster
```

### Running the Worker in Production Mode

For production, include the Django settings module environment variable:

```
docker run --rm \
    -v ${PWD}/logs:/app/logs \
    -v ${PWD}/cache:/app/cache \
    -v ${PWD}/db:/app/db \
    -v ${PWD}/media:/app/media \
    -v ${PWD}/static:/app/static \
    -e DJANGO_SETTINGS_MODULE="pyaa.settings.prod" \
    pyaa python3 manage.py qcluster
```

## Docker Compose Example

For Docker Compose, you can add a dedicated worker service:

```yml
services:
  # Other services...

  pyaa-worker:
    build:
      context: pyaa
      dockerfile: Dockerfile
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
```

This command runs `python3 manage.py qcluster`, which starts the django-q2 cluster for processing queue tasks.