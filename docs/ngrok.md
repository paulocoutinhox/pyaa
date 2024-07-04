# NGROK

Install `ngrok` from their documentation: https://dashboard.ngrok.com/get-started/setup.

Setup your `ngrok` auth token:

```bash
ngrok config add-authtoken xyz
```

or edit configuration using:

```bash
ngrok config edit
```

## Start app with ngrok domain

Get your static domain from `ngrok` endpoints.

Start application with `ngrok` domain:

```bash
APP_CSRF_TRUSTED_ORIGINS=https://*.ngrok-free.app python3 manage.py runserver
```

or

```bash
export APP_ALLOWED_HOSTS=ngrok-free.app
export APP_CSRF_TRUSTED_ORIGINS=https://xyz.ngrok-free.app
python3 manage.py runserver "0.0.0.0:8000"
```
