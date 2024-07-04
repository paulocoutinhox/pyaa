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
		-p 8000:8000 pyaa
```

## References

- [Security](docs/security.md)
- [Ngrok](docs/ngrok.md)
- [API](docs/api.md)
- [Troubleshooting](docs/troubleshooting.md)

## License

[MIT](http://opensource.org/licenses/MIT)

Copyright (c) 2024, Paulo Coutinho
