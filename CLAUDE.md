# CLAUDE.md

Reference for AI agents and developers working in this repository. It captures the
structure, conventions, and patterns that are **not obvious from reading a single file**,
so you can navigate straight to the right place instead of scanning the whole tree.

## Project

PyAA is a **Django 6.0** project with an **async FastAPI** layer mounted on the same ASGI
app. Django serves the site and admin (WSGI). FastAPI serves the JSON API under `/api`.
Background jobs run on **django-q2**. Frontend assets are built with **Vite + Tailwind v4**.
Target runtime: **Python 3.12+**. Two locales: `en`, `pt-br`.

Request flow (`pyaa/asgi.py`): one `FastAPI` app, with API routers mounted at
`PYAA_API_PREFIX` (`/api`), and everything else falling through to the Django WSGI app
mounted at `/` via `WSGIMiddleware`. Django is the catch-all. FastAPI only owns `/api`.

## IMPORTANT — code style (YOU MUST follow)

These are project rules that override defaults. Apply them to every edit.

- Code and comments are in **English**.
- Keep **functions, methods, constructors, and calls on a single line**. Never wrap
  parameters vertically, even with many arguments.
- Single-line comments starting with `#` or `//` are **lowercase**. Multi-sentence comments
  use normal capitalization and full punctuation, one complete sentence per line.
- Comments are **rare** and explain intent, not the obvious. No decorative section banners
  ("helpers", "validators"). No comments restating the code.
- **No** back-compat shims, legacy code, or version-compat checks. Write the final version.
- **No** `TYPE_CHECKING` import guards.
- **No** semicolons joining statements or sentences.
- `__init__.py` files stay **completely empty**.
- Separate logical blocks in a method with a single blank line. Avoid excess vertical space.
- Format with `black` (`make format`).

## Commands

```
make deps            # install python deps (requirements.txt)
make setup           # create runtime dirs: logs cache db static media
make migrate         # makemigrations + migrate
make frontend-setup  # npm install
make frontend-prod   # vite build (produces hashed assets + manifest)
make run             # dev server (WSGI runserver)
make run-async       # uvicorn pyaa.asgi:application
make run-worker      # django-q qcluster
make test            # Django unittest suite (manage.py test)
make test-api        # API tests (pytest, apps/api)
make format          # black .
```

Asset build is handled entirely by Vite (`make frontend-prod`).

## Directory map

- `pyaa/` — project core (settings, asgi/wsgi, admin site, mixins, fields, filters, helpers,
  context processors, sitemaps, `fastapi/`).
- `apps/<name>/` — business apps (see table).
- `templates/`, `locale/{en,pt}/LC_MESSAGES/`, `apps/web/static/` — templates, translations, assets.

| App | Purpose | API router |
|-----|---------|:----------:|
| `user` | Custom `AUTH_USER_MODEL` (`user.User`), `MultiFieldModelBackend`, `createadmin` cmd | schemas only |
| `customer` | Customer profile, addresses, credits, activation/recovery tokens | ✅ |
| `shop` | Plans, subscriptions, credit/product purchases, Stripe gateway (`gateways/stripe.py`) | ✅ |
| `banner` | Ad banners by zone + access logging | ✅ |
| `gallery` | Image galleries | ✅ |
| `content` | CMS content pages | ✅ |
| `language` | Language model + fixtures | ✅ |
| `system_log` | Structured system logging | ✅ |
| `auth` (api) | JWT login/refresh (`apps/api/auth`) | ✅ |
| `newsletter` | Newsletter subscriptions | — |
| `report` | Admin-only reports (`report/admin/` package, no models) | — |
| `site` | Site-wide config model | — |
| `backup` | DB backup/restore management commands only | — |
| `web` | Public frontend (`views/` pkg, `forms/`, `templatetags/`, `urls.py`, no models) | — |

## Per-app file layout

Each app is `apps.<name>` (`apps.py`: `name = "apps.<name>"`, `verbose_name = _("apps.<name>.description")`).
Files appear only when needed: `models.py`, `admin.py`, `enums.py`, `helpers.py`, `forms.py`,
`filters.py`, `fields.py`, `migrations/`, `fixtures/`, `tests/`. API apps add `routes.py` and
`schemas.py` under `apps/api/<name>/`.

## Patterns by layer

Read the **canonical example** listed, then mirror it. Do not invent a new shape.

### Models — canonical: `apps/customer/models.py`
- Explicit `Meta` with `db_table`, `verbose_name`/`verbose_name_plural` as **i18n keys**.
- Explicit `id = models.BigAutoField(_("model.field.id"), unique=True, primary_key=True)`.
- Field labels are gettext_lazy **keys**: `_("model.field.<name>")`, never English text.
- `indexes` in `Meta`, named from the `db_table` var.
- `__str__` returns a real value with fallback, often an i18n key.
- Validation lives in `clean()`, which calls `super().clean()` and raises
  `ValidationError({...})`. Unsaved defaults go in `setup_initial_data()`. `save()` runs
  `setup_initial_data()`, then `full_clean()`, then `super().save(...)`.
- Heavy logic delegates to helpers. Models expose thin domain methods (`has_credits()` …).

### Enums — canonical: `apps/customer/enums.py`
- `TextChoices` subclasses: `NAME = "value", _("enum.<enum-name>.<name>")`.
- Every enum defines `get_choices()` returning `tuple((i.name, i.value) for i in cls)`.
- **YOU MUST keep `get_choices()`**. It is asserted by `apps/<app>/tests/test_enums.py`.

### Admin — canonical: `apps/customer/admin.py`. Badges: `apps/shop/admin.py`
- Shared mixins in `pyaa/mixins.py`: `ReadonlyLinksMixin` (FKs in `readonly_fields_links`
  render as clickable change-links) and `SanitizeDigitFieldsMixin` (`digit_only_fields`).
- Computed columns via `@admin.display(ordering=..., description=_("model.field.x"))`, with
  `boolean=True` for flags.
- **Admin classes MUST group fields with `fieldsets`** (never a flat `fields` list). Each
  section title is an i18n key whose translated value is **UPPERCASE**
  (`_("admin.fieldsets.user")` → `USER INFORMATION`, `_("admin.fieldsets.general")` → `GENERAL`).
- Status/level badges call `StatusHelper.get_status_color(value, "hex")` (`pyaa/helpers/status.py`)
  and render with `format_html`. The same helper colors the frontend
  (`apps/web/templatetags/pyaa_status.py`).
- The admin site is customized in `pyaa/admin.py` (`AppAdmin(AdminSite)`, custom
  `get_app_list()` grouping, captcha login), wired by `pyaa/apps.py` `AppAdminConfig`.

### Helpers — canonical: `apps/customer/helpers.py`, `pyaa/helpers/*`
- Static-method classes, never instantiated. Per-app in `apps/<app>/helpers.py`. Cross-cutting
  in `pyaa/helpers/` (`EmailHelper`, `StatusHelper`, `FormatHelper`, `StringHelper`,
  `database.py`, `file.py`, `request.py`, `system.py`).
- Transactional helpers add `@transaction.atomic`. Called by class name from admin, models,
  views, and API routes.

### API layer — canonical: `apps/api/customer/{routes,schemas}.py`
- `pyaa/fastapi/routes.py` assembles one `APIRouter`, with one `include_router` per domain
  using `prefix` and `tags`.
- Schemas subclass `pyaa/fastapi/schemas.BaseSchema`
  (`from_attributes=True, populate_by_name=True, alias_generator=to_camel`). ORM objects
  validate directly and **JSON is camelCase** (`firstName`) while Python stays snake_case.
  Non-trivial fields use `@field_serializer`. Response schemas compose and extend.
- Routes are `async def`. Reads use the **async ORM** (`await ...aget/acount/acreate`).
  Multi-step writes go in a sync function decorated `@sync_to_async` + `@transaction.atomic`
  and are awaited (`_create_customer_transaction`).
- Auth: `apps/api/auth/dependencies.py` exports
  `CurrentUser = Annotated[User, Depends(get_current_user)]` (authentication only) and
  `require_permission("<app>.<action>_<model>")` (authorization). Tokens are minted in
  `pyaa/fastapi/jwt.py` (HS256, signed with `SECRET_KEY`).
- **Write/admin endpoints MUST require a user that holds the permission for the action**, not
  just any authenticated user. Gate them with
  `dependencies=[Depends(require_permission("content.add_content"))]` (see
  `apps/api/content/routes.py`). Use `CurrentUser` alone only for self-service on the caller's
  own data (e.g. `apps/api/customer/routes.py` profile update), and leave genuinely public
  flows (login, signup, tracking) ungated.
- `pyaa/fastapi/rate_limiter.py` throttles only paths under `settings.PYAA_API_PREFIX`
  (`ConditionalLimiterMiddleware`). `pyaa/fastapi/language.py` activates translation per request.
- Stripe webhooks (`apps/shop/gateways/stripe.py`) are idempotent through the unique
  `EventLog.event_id`, so a retried delivery is skipped.

### Settings — `pyaa/settings/dev.py` (base) + `pyaa/settings/prod.py`
- `prod.py` does `from .dev import *` then overrides (`DEBUG`, `SECRET_KEY`, `DATABASES`,
  security/HSTS, Anymail/SES, file cache, error logging). `asgi.py` and `pytest.ini` default
  to `pyaa.settings.dev`.
- Config is read via `os.getenv("APP_*", default)`. Notable:
  - Feature toggles: `PYAA_API_PREFIX` (`APP_API_PREFIX`, default `/api`),
    `PYAA_ENABLE_FASTAPI`, `PYAA_ENABLE_DJANGO`.
  - Env: `APP_ALLOWED_HOSTS`, `APP_CSRF_TRUSTED_ORIGINS`, `APP_MEDIA_URL`,
    `APP_GOOGLE_ANALYTICS_ID`, plus `AWS_*`, `STRIPE_SECRET_KEY`/`STRIPE_WEBHOOK_SECRET`,
    `RECAPTCHA_*`, `CI`.
  - Core: `AUTH_USER_MODEL="user.User"`, `AUTHENTICATION_BACKENDS` = `MultiFieldModelBackend`,
    `AUTH_JWT` (HS256, `SIGNING_KEY=SECRET_KEY`), `SITE_ID=1`,
    `DEFAULT_TIME_ZONE="America/Sao_Paulo"`, `STORAGES` (filesystem default + `s3`), `Q_CLUSTER`,
    `CUSTOMER_SIGNUP_PLAN`/`CUSTOMER_ACTIVATION_REQUIRED`, `BANNER_ACCESS_INTERVAL`.
- `INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + PROJECT_APPS`.

### i18n — `locale/{en,pt}/LC_MESSAGES/django.po`
- **All** user-facing strings are translation keys, never inline English. Namespaces:
  `site.*`, `admin.*`, `apps.<app>.description`, `model.<model>.name[.plural]`,
  `model.field.*`, `model.str.*`, `enum.<enum-name>.*`, `error.*`, `email.*`, `message.*`,
  `title.*`. Keys are dot-and-hyphen delimited (`model.field.mobile-phone`). Add the key to
  both locale files when adding strings. The API honors i18n per request via
  `pyaa/fastapi/language.py`.

### Background jobs
- `EmailHelper.send_email_async` (`pyaa/helpers/email.py`) wraps `django_q.tasks.async_task`.
  All transactional emails go through it from `CustomerHelper`. Worker: `make run-worker`
  (`qcluster`). `crontab` runs `manage.py check` each minute (cron container).

### Frontend
- Vite + Tailwind v4 + PostCSS + daisyUI. `vite.config.js` uses root
  `apps/web/static/vendor/frontend`, base `/static/frontend/`, and outputs hashed files plus a
  `manifest` to `apps/web/static/frontend`. `tailwind.config.js` scans `templates/**/*.html`
  and frontend JS.

### Web routing & templates
- Root URLconf `pyaa/urls.py` mounts admin, sitemaps, static/media, and `include`s the web
  URLs. `apps/web/urls.py` builds `urlpatterns` by concatenating the `urlpatterns` exported by
  each module under `apps/web/views/` (`home`, `account`, `content`, `gallery`, `contact`,
  `shop/`, `banner`, `newsletter`). A new public page = a new `apps/web/views/<feature>.py`
  that defines its view functions and its own `urlpatterns`, added in `apps/web/urls.py`.
- `templates/` is shared (not per-app): `pages/`, `partials/`, `layouts/`, `emails/`,
  `admin/`, `pyaa/`. `APP_DIRS` is off, so all templates live here.
- Payments are gateway-abstracted in `apps/shop/gateways/` (`stripe.py`). Gateway selection is
  driven by settings (`GATEWAY_FOR_PRODUCT_PURCHASE`). The Stripe webhook entrypoint is the
  web view `apps/web/views/shop/shop_webhook.py`.
- Fixtures: apps that need seed data ship `fixtures/initial.json` (`content`, `language`,
  `site`). `make fixtures` runs `loaddata initial`. Custom management commands live in
  `apps/<app>/management/commands/` (`createadmin` in `user`, `backup_db`/`restore_db` in
  `backup`).

## Tests

Two systems:
- **Django apps** — unittest via `make test`. Per-app `tests/` package with granular files
  (`test_models.py`, `test_admin.py`, `test_forms.py`, `test_filters.py`, `test_enums.py` …).
  Project-level tests live in `pyaa/tests/`.
- **API** — pytest (`pytest.ini`, `testpaths = apps/api`, settings = dev). Domain tests are
  `apps/api/<app>/tests.py`. `apps/api/conftest.py` provides `app`, `client`
  (`TestClient` over `transactional_db`), and an autouse `load_fixtures` (`loaddata initial`).
  **Authenticate** by minting `create_access_token(test_user)` and sending
  `headers={"Authorization": f"Bearer {token}"}`. Request bodies are **camelCase**.

## Docker / deployment

Per-role images run one process each and rely on Docker to restart them:
- `Dockerfile.web` runs uWSGI (`app-entrypoint.sh`). `Dockerfile.async.web` runs
  Gunicorn+Uvicorn (`app-async-entrypoint.sh`). `Dockerfile.cron` runs cron
  (`cron-entrypoint.sh`). The worker uses `worker-entrypoint.sh` (`qcluster`).

All-in-one images run web + cron + worker in one container under **supervisord**:
- `Dockerfile.all.web` (sync) and `Dockerfile.all.async.web` (async). The
  `app-all*-entrypoint.sh` scripts run the one-time bootstrap (migrate, build assets,
  collectstatic, export env) and then `exec supervisord`. The `supervisord.all*.conf` files
  run `cron`/`worker`/`web` in the foreground with `autorestart=true`. Supervisord is PID 1
  for clean shutdown, zombie reaping, and `supervisorctl`. These images run as **root**
  because the cron daemon requires it.

## Gotchas

- Django owns every non-`/api` route. The FastAPI app is only the API plus the WSGI mount.
- `get_choices()` on enums is public and tested API, not dead code.
- Admin readonly link fields (`ReadonlyLinksMixin`) render via callables in `readonly_fields`,
  not plain field-name strings.
- `prod.py` ships as a template (SQLite, placeholder secret, commented email backend). Real
  production values are supplied per deployment.
