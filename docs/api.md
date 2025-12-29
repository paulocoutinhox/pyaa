# API

The PyAA project uses **FastAPI** as the web framework for building high-performance REST APIs with automatic OpenAPI documentation.

## Architecture

### Directory Structure

```
apps/api/
├── __init__.py
├── conftest.py                    # Pytest configuration for FastAPI tests
├── auth/
│   ├── dependencies.py            # JWT authentication dependency
│   ├── routes.py                  # Token endpoints (pair, refresh)
│   ├── schemas.py                 # Pydantic models for auth
│   └── tests.py                   # FastAPI tests
├── customer/
│   ├── routes.py                  # Customer CRUD endpoints
│   ├── schemas.py                 # Pydantic models for customer
│   └── tests.py                   # FastAPI tests
├── banner/
│   ├── routes.py                  # Banner endpoints
│   ├── schemas.py                 # Pydantic models for banner
│   └── tests.py                   # FastAPI tests
└── [other modules...]

pyaa/fastapi/
├── __init__.py
├── routes.py                      # Main router that includes all app routers
├── jwt.py                         # Native JWT implementation
├── schemas.py                     # Base Pydantic schemas
├── cors.py                        # CORS configuration
└── rate_limiter.py                # Rate limiting configuration
```

### Configuration

The FastAPI application is configured in `/pyaa/fastapi/routes.py` which aggregates all module routers:

```python
from fastapi import APIRouter

router = APIRouter()

router.include_router(auth_router, prefix="/token", tags=["Authentication"])
router.include_router(customer_router, prefix="/customer", tags=["Customer"])
router.include_router(language_router, prefix="/language", tags=["Language"])
# ... other routers
```

The main FastAPI app is mounted in `/pyaa/asgi.py` and integrated with Django via `WSGIMiddleware`.

### Environment Variables

The following environment variables control the API and application behavior:

| Variable | Default | Description |
|----------|---------|-------------|
| `APP_API_PREFIX` | `/api` | URL prefix for all FastAPI routes (e.g., `/api/customer`, `/api/token/pair`) |
| `APP_ENABLE_FASTAPI` | `true` | Enable or disable FastAPI routes and documentation endpoints |
| `APP_ENABLE_DJANGO` | `true` | Enable or disable Django WSGI application (admin, traditional views) |

**Example usage in `.env`:**

```bash
APP_API_PREFIX=/api
APP_ENABLE_FASTAPI=true
APP_ENABLE_DJANGO=true
```

These variables are used in `/pyaa/asgi.py` to configure which parts of the application are active and how routes are mounted.

### Static and Media Files in Production

In production (when `DEBUG=False`), FastAPI automatically serves static and media files if their URLs start with `/`:

**Configuration:**
- Static files are served from `STATIC_ROOT` at `STATIC_URL` path
- Media files are served from `MEDIA_ROOT` at `MEDIA_URL` path
- Only activated in production mode (`not DEBUG`)
- Only when URLs start with `/` (configurable behavior)
- FastAPI mounts these paths before Django's WSGIMiddleware catchall

**Example settings:**
```python
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"
```

## Creating New API Endpoints

### 1. Define Pydantic Schemas

Create schemas in `apps/api/[module]/schemas.py`:

```python
from pydantic import EmailStr
from pyaa.fastapi.schemas import BaseSchema

class CustomerCreateSchema(BaseSchema):
    email: EmailStr
    password: str
    language: int
    timezone: str

class CustomerResponseSchema(BaseSchema):
    user: UserSchema
    language: LanguageSchema | None
    timezone: str | None
    created_at: datetime | None
```

### 2. Create Routes

Create routes in `apps/api/[module]/routes.py`:

```python
from fastapi import APIRouter, HTTPException, status
from apps.api.auth.dependencies import CurrentUser

router = APIRouter()

@router.post("/", response_model=CustomerCreateResponseSchema, status_code=status.HTTP_201_CREATED)
def create_customer(data: CustomerCreateSchema):
    # implementation
    return response

@router.get("/me/", response_model=CustomerResponseSchema)
async def get_customer_me(user: CurrentUser):
    # use async when making async django orm calls
    customer = await Customer.objects.select_related("language").aget(user=user)
    return customer
```

### 3. Register Router

Add your router to `/pyaa/fastapi/routes.py`:

```python
from apps.api.mymodule.routes import router as mymodule_router

router.include_router(mymodule_router, prefix="/mymodule", tags=["My Module"])
```

## Authentication

### JWT Implementation

PyAA uses a **native JWT implementation** with PyJWT (`/pyaa/fastapi/jwt.py`):

```python
from pyaa.fastapi.jwt import create_access_token, create_refresh_token, get_user_from_token

# create tokens
access_token = create_access_token(user)
refresh_token = create_refresh_token(user)

# verify and get user from token
user = get_user_from_token(access_token)
```

### Protected Endpoints

Use the `CurrentUser` dependency for protected routes:

```python
from apps.api.auth.dependencies import CurrentUser

@router.get("/me/")
def get_current_user_data(user: CurrentUser):
    # user is automatically injected from JWT token
    return {"email": user.email}
```

The `CurrentUser` dependency:
- Extracts the JWT token from `Authorization: Bearer <token>` header
- Validates the token signature and expiration
- Fetches the user from database
- Returns `401 Unauthorized` if token is invalid or user not found

## Async Support

FastAPI supports both **sync** and **async** endpoints:

### Synchronous Endpoints (Blocking I/O)

```python
@router.post("/")
def create_customer(data: CustomerCreateSchema):
    # sync django orm calls
    user = User.objects.create(email=data.email)
    customer = Customer.objects.create(user=user)
    return customer
```

### Asynchronous Endpoints (Non-blocking I/O)

```python
@router.get("/me/")
async def get_customer_me(user: CurrentUser):
    # async django orm calls (use aget, afilter, etc.)
    customer = await Customer.objects.select_related("language").aget(user=user)
    return customer
```

**When to use async:**
- Database queries that can benefit from async ORM methods (`aget`, `afilter`, `acreate`)
- External API calls with async HTTP clients
- I/O-bound operations

**When to use sync:**
- Simple CRUD operations
- Operations that use Django's sync ORM heavily
- When performance difference is negligible

## Testing

### Test Structure

Tests use **pytest** with **FastAPI TestClient** (`apps/api/[module]/tests.py`):

```python
import pytest

def test_create_customer(client):
    customer_data = {
        "email": "test@example.com",
        "password": "password123",
        "language": 1,
        "timezone": "America/Sao_Paulo",
    }

    response = client.post("/api/customer", json=customer_data)

    assert response.status_code == 201
    data = response.json()
    assert data["user"]["email"] == "test@example.com"

def test_get_customer_me(client, customer, access_token):
    response = client.get(
        "/api/customer/me",
        headers={"Authorization": f"Bearer {access_token}"}
    )

    assert response.status_code == 200
```

### Pytest Fixtures

Common fixtures are defined in `/apps/api/conftest.py`:

- `app`: FastAPI application instance
- `client`: TestClient for making requests
- `transactional_db`: Database with transaction rollback after each test

### Running Tests

```bash
# run all API tests
make test-api

# run with coverage
make test-api-coverage

# run specific test file
pytest apps/api/customer/tests.py -v

# run specific test
pytest apps/api/customer/tests.py::test_create_customer -v
```

### Automatic Documentation

FastAPI automatically generates interactive API documentation:

- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc
- **OpenAPI JSON**: http://localhost:8000/api/openapi.json

The documentation is generated from:
- Pydantic schemas (request/response models)
- Route decorators (HTTP methods, status codes)
- Python docstrings
- Type hints

## Standard Response Formats

### Single Get Object Response

**Code**: `200 OK`
**Method**: `GET`

```json
{
    "id": 1,
    "name": "Test"
}
```

### Single Create Object Response

**Code**: `201 Created`
**Method**: `POST`

```json
{
    "id": 1,
    "name": "Test"
}
```

### Single Update Object Response

**Code**: `200 OK`
**Method**: `PUT` or `PATCH`

```json
{
    "id": 1,
    "name": "Updated Test"
}
```

### Single Delete Object Response

**Code**: `204 No Content`
**Method**: `DELETE`

### List Response with Pagination

**Code**: `200 OK`
**Method**: `GET`

```json
{
    "count": 25,
    "items": [
        {
            "id": 1,
            "name": "Test"
        },
        {
            "id": 2,
            "name": "Test 2"
        }
    ]
}
```

**Query Parameters:**
- `limit`: Number of items per page (default: 100, max: 1000)
- `offset`: Starting position (default: 0)

Example: `GET /api/language?limit=10&offset=20`

## Error Responses

### Validation Error

**Code**: `422 Unprocessable Entity`
**Method**: `POST`, `PUT`, `PATCH`

```json
{
    "detail": [
        {
            "user": {
                "email": ["Enter a valid email address."]
            }
        }
    ]
}
```

FastAPI uses Pydantic for request validation. Invalid data automatically returns detailed error messages.

### Authentication Error

**Code**: `401 Unauthorized`
**Method**: Any protected endpoint

```json
{
    "detail": "Token is invalid or expired"
}
```

Common authentication errors:
- Missing or invalid token format
- Expired token
- User not found
- Invalid signature

### Authorization Error

**Code**: `403 Forbidden`
**Method**: Any

```json
{
    "detail": "You do not have permission to perform this action"
}
```

### Not Found Error

**Code**: `404 Not Found`
**Method**: Any

```json
{
    "detail": "Customer not found."
}
```

### Rate Limit Error

**Code**: `429 Too Many Requests`
**Method**: Any

```json
{
    "detail": "Rate limit exceeded"
}
```

## Authentication Endpoints

### Token Pair (Login)

**Endpoint**: `POST /api/token/pair`
**Authentication**: Not required

**Request:**
```json
{
    "login": "user@example.com",
    "password": "password123"
}
```

**Success Response** (`200 OK`):
```json
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Error Response** (`401 Unauthorized`):
```json
{
    "detail": "No active account found with the given credentials"
}
```

### Token Refresh

**Endpoint**: `POST /api/token/refresh`
**Authentication**: Not required

**Request:**
```json
{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Success Response** (`200 OK`):
```json
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Error Response** (`401 Unauthorized`):
```json
{
    "detail": "Token is invalid or expired"
}
```

## Best Practices

### 1. Use Pydantic Schemas

Always define request/response schemas using Pydantic:

```python
# Good
@router.post("/", response_model=CustomerResponseSchema)
def create_customer(data: CustomerCreateSchema):
    pass

# Bad
@router.post("/")
def create_customer(data: dict):
    pass
```

### 2. Use Proper HTTP Status Codes

```python
from fastapi import status

@router.post("/", status_code=status.HTTP_201_CREATED)
@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
@router.get("/", status_code=status.HTTP_200_OK)
```

### 3. Handle Exceptions Properly

```python
from fastapi import HTTPException, status

try:
    customer = Customer.objects.get(user=user)
except Customer.DoesNotExist:
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Customer not found."
    )
```

### 4. Use Async When Appropriate

```python
# Async for database queries
@router.get("/me/")
async def get_customer(user: CurrentUser):
    customer = await Customer.objects.aget(user=user)
    return customer

# Sync for simple operations
@router.post("/")
def create_customer(data: CustomerCreateSchema):
    return Customer.objects.create(**data.dict())
```

### 5. Use Dependencies for Reusable Logic

```python
from apps.api.auth.dependencies import CurrentUser

@router.get("/")
def get_data(user: CurrentUser):  # Automatically handles JWT authentication
    return {"user_id": user.id}
```

### 6. Write Comprehensive Tests

- Test all endpoints (happy path and error cases)
- Use fixtures for common setup
- Aim for 100% code coverage
- Test authentication and authorization

```python
def test_create_customer_validation_error(client):
    response = client.post("/api/customer", json={"email": "invalid"})
    assert response.status_code == 422
```

### 7. Document Your Endpoints

Use docstrings and type hints for better auto-generated documentation:

```python
@router.post("/", response_model=CustomerResponseSchema)
def create_customer(data: CustomerCreateSchema):
    """
    Create a new customer account.

    Returns the created customer with access and refresh tokens.
    """
    pass
```
