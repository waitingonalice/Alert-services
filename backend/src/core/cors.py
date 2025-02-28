from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings


class CustomCORSMiddleware:
    """
    Custom CORs middleware to allow only specific origins
    """

    def __init__(self, app: FastAPI):
        # Hardcoded origins are required (swap with env vars in the future) because withCredentials header is used on frontend for httpOnly cookies. Usage of Access-Control-Allow-Origin wildcard will be not permitted.
        # Refer to docs: https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS/Errors/CORSNotSupportingCredentials
        self.origins = [
            "http://localhost:5173",
            "http://localhost:5174",
            settings.FRONTEND_URL,
        ]
        self.methods = ["PATCH", "OPTIONS", "GET", "POST", "PUT", "HEAD"]
        self.app = app

    def add_middleware(self):
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=self.origins,
            allow_credentials=True,
            allow_methods=self.methods,
            allow_headers=["*"],
        )
