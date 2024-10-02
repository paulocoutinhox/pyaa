# API

The PyAA project is configured to use Django Rest Framework.

All URLs to the APIs are inside path `DOMAIN + API + RESOURCE`, example:

```
http://localhost:8000/api/customer
```

Most resources are protected by authentication header `Authorization: Bearer XYZ` with view property in Python `permission_classes = [AppModelPermissions]`. But if you need allow public access to some resource view use `permission_classes = [AllowAny]`.

The token APIs to create and refresh are `http://localhost:8000/api/token/` and `http://localhost:8000/api/token/refresh/`.

The schema can be acessed by:
- http://localhost:8000/api/schema
- http://localhost:8000/api/schema/redoc
- http://localhost:8000/api/schema/swagger-ui

## Single Get Object Response

Code Http: `200`
Method Http: `GET`

Sample of response structure:

```json
{
    "id": 1,
    "name": "Test"
}
```

## Single Create Object Response

Code Http: `201`
Method Http: `POST`

Sample of response structure:

```json
{
    "id": 1,
    "name": "Test"
}
```

## Single Update Object Response

Code Http: `200`
Method Http: `PUT`

Sample of response structure:

```json
{
    "id": 1,
    "name": "Test"
}
```
## Single Delete Object Response

Code Http: `204`
Method Http: `DELETE`

## Object Get List Response

Code Http: `200`
Method Http: `GET`

Sample of response structure:

```json
{
    "count": 3,
    "next": "http://localhost:8000/api/resource-name/?limit=1&offset=1",
    "previous": null,
    "results": [
        {
            "id": 1,
            "name": "Test"
        }
    ]
}
```

## Object Validation Response

Code Http: `400`
Method Http: `POST` and `PUT`

Sample of response structure:

```json
{
    "email": [
        "cliente com este email já existe."
    ]
}
```

## Authentication Error Response

Code Http: `401`
Method Http: `Any`

Sample of response structure:

```json
{
    "detail": "Given token not valid for any token type",
    "code": "token_not_valid",
    "messages": [
        {
            "token_class": "AccessToken",
            "token_type": "access",
            "message": "Token is invalid or expired"
        }
    ]
}
```

## Not Found Response

Code Http: `404`
Method Http: `Any`

Sample of response structure:

```json
{
    "detail": "Not found."
}
```

## Login Token Success Response

Code Http: `200`
Method Http: `POST`

Sample of response structure:

```json
{
    "refresh": "abc.def.ghi",
    "access": "abc.def.ghi"
}
```

## Login Token Validation Response

Code Http: `400`
Method Http: `POST`

Sample of response structure:

```json
{
    "username": [
        "This field is required."
    ],
    "password": [
        "This field is required."
    ]
}
```

## Login Token Error Response

Code Http: `401`
Method Http: `POST`

Sample of response structure:

```json
{
    "detail": "No active account found with the given credentials"
}
```

## Refresh Token Success Response

Code Http: `200`
Method Http: `POST`

Sample of response structure:

```json
{
    "access": "abc.def.ghi"
}
```

## Refresh Token Validation Response

Code Http: `400`
Method Http: `POST`

Sample of response structure:

```json
{
    "refresh": [
        "This field is required."
    ]
}
```

## Refresh Token Error Response

Code Http: `401`
Method Http: `POST`

Sample of response structure:

```json
{
    "detail": "Token is invalid or expired",
    "code": "token_not_valid"
}
```
