# PyAA

Template application that use Python + Django to build any application with common modules.

## How to use

Execute the following commands:

```
make setup
make migrate
make create-su
make fixtures
make run
```

## Docker

This project have a ready for production docker file.

Execute the following commands:

```
make docker-build
make docker-run
```

or:

```
make docker-build
make docker-run-prod
```

## Docker volumes

By default, this project use SQLite database and store it inside `db` folder created automatically.

By default, this project store uploads inside `media` folder created automatically.

You need pass your volumes paths in production. Example:

```
docker build --no-cache -t pyaa .

docker run --rm -v ${PWD}/db:/app/db \
		-v ${PWD}/media:/app/media \
		-e APP_ENV=dev \
		-e DJANGO_SUPERUSER_USERNAME="admin" \
		-e DJANGO_SUPERUSER_EMAIL="admin@admin.com" \
		-e DJANGO_SUPERUSER_PASSWORD="admin" \
		-p 8000:8000 pyaa
```

## Environment

You need change some environment variables:

```
APP_ENV=prod
APP_ALLOWED_HOSTS=".mydomain.com"
APP_CSRF_TRUSTED_ORIGINS="https://*.mydomain.com"

APP_MEDIA_URL=/media/

DJANGO_SUPERUSER_USERNAME="admin"
DJANGO_SUPERUSER_EMAIL="admin@admin.com"
DJANGO_SUPERUSER_PASSWORD="admin"
```

Obs: Obviously you must change this data for your real data, referring to your server.

## References

- [Security](docs/security.md)
- [Ngrok](docs/ngrok.md)
- [API](docs/api.md)
- [Troubleshooting](docs/troubleshooting.md)

## License

[MIT](http://opensource.org/licenses/MIT)

Copyright (c) 2024, Paulo Coutinho
