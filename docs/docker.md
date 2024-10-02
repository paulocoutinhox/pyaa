# Docker

This project includes a production-ready Dockerfile.

You need to set up the project files before using Docker with the following command:

```
make setup
```

Next, configure Docker by executing the following commands:

```
make docker-build
make docker-run
```

or:

```
make docker-build
make docker-run-prod
```

Finally, set up the fixtures and create the Super User with the following commands:

```
docker exec -it pyaa make fixtures
docker exec -it pyaa make create-su
```

## Docker volumes

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
    -p 8000:8000 pyaa
```

## Docker compose

You can use this configuration when use Docker Compose:

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
      dockerfile: Dockerfile
    restart: always
    depends_on:
      - mysql
    environment:
      - DJANGO_SETTINGS_MODULE=pyaa.settings.prod
      - APP_ALLOWED_HOSTS=your-domain.com
      - APP_CSRF_TRUSTED_ORIGINS=https://your-domain.com
      - APP_PAYMENT_HOST=your-domain.com
    volumes:
      - ./pyaa/logs:/app/logs
      - ./pyaa/cache:/app/cache
      - ./pyaa/db:/app/db
      - ./pyaa/media:/app/media

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
