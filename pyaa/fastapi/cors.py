from django.conf import settings
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


def setup(app: FastAPI):
    # restrict credentialed cross-origin access to the configured origins
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
