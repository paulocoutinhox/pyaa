# Production

There are some settings you need to configure to deploy the application in the production environment.

You need change some environment variables for production environment:

```
APP_ALLOWED_HOSTS=".mydomain.com"
APP_CSRF_TRUSTED_ORIGINS="https://*.mydomain.com"
APP_MEDIA_URL=/media/
```

Alternatively, you can define `MEDIA_URL` directly in `pyaa/settings/prod.py`, similar to the S3 storage example:

```python
# in pyaa/settings/prod.py
MEDIA_URL = f"https://{STORAGES['default']['OPTIONS']['bucket_name']}.s3.amazonaws.com/"
```

Obs: Obviously you must change this data for your real data, referring to your server.

## Super Admin User

The super admin user is typically created using the command `make create-su`, with the default email `admin@admin.com` and password `admin`.

You need to log into the admin panel using this account, and then update the email and password to the ones you wish to use.
