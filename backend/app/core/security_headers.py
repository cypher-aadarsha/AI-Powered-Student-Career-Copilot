"""Defensive HTTP response headers, applied to every response. This is an
API-only backend (no HTML templates rendered here), so there's no
Content-Security-Policy to write — the frontend's own responses are what a
browser actually renders — but the headers below still matter for a browser
that ever hits this API directly (e.g. a fetched JSON error page, a
downloaded resume) and cost nothing to always send.
"""
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, *, enable_hsts: bool):
        super().__init__(app)
        self.enable_hsts = enable_hsts

    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), camera=(), microphone=()"
        if self.enable_hsts:
            # Only meaningful once the deployment terminates HTTPS in front of
            # this app — sending it over plain HTTP (e.g. local dev) is inert.
            response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains"
        return response
