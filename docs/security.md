# Security

## Configure before production

These values ship with development defaults and must be reviewed for a real deployment:

- **Secret key**: change `SECRET_KEY` in `pyaa/settings/prod.py`. It also signs the JWT tokens (`AUTH_JWT["SIGNING_KEY"]`), so never ship the default.
- **Allowed hosts**: set `APP_ALLOWED_HOSTS` (comma-separated) in the environment so `ALLOWED_HOSTS` is not left open.
- **CORS**: the API CORS is permissive by default. For production, restrict it to the trusted origins (`APP_CORS_ALLOWED_ORIGINS`).
- **JWT lifetimes**: configure `ACCESS_TOKEN_LIFETIME` and `REFRESH_TOKEN_LIFETIME` in `AUTH_JWT`. Prefer short-lived access tokens and a moderate refresh window in production.

## Built-in protections

These are enforced in the code:

- **Authentication**: `is_active` is verified on JWT access and refresh, so deactivated accounts lose API access immediately.
- **Login throttling**: failed logins are rate limited per IP via `LOGIN_RATELIMIT_MAX_ATTEMPTS` and `LOGIN_RATELIMIT_WINDOW` (cache backed).
- **Password recovery**: recovery tokens expire after `PASSWORD_RECOVERY_TOKEN_TTL` (default 1 hour).
- **Password strength**: `AUTH_PASSWORD_VALIDATORS` are enforced on signup, password reset, password change and the customer API.
- **Editor uploads**: the `/upload-image/` endpoint requires an authenticated staff user and validates that the uploaded file is a real image.
- **Payments**: the Stripe webhook verifies the signature (`STRIPE_WEBHOOK_SECRET`); checkout prices come from the server-side plan/product, never from the request.
- **Ownership**: account resources (subscriptions, purchases, credits) are always scoped to the authenticated customer.
