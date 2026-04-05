"""
app/core/security.py
--------------------
Security utilities for the application.

Handles:
- CORS (Cross-Origin Resource Sharing) headers
  → Allows the HTML UI or any frontend to call our API
- Security response headers
  → Good practice to always send these

In a real production app, this would also hold:
- JWT token validation
- OAuth2 logic
- API key checking
For this project, we just handle CORS.
"""

from flask import request


def add_cors_headers(response):
    """
    Add CORS headers to every response so any frontend can call this API.

    Without this, a browser will BLOCK the request with:
    "Access to fetch at 'http://localhost:5000' from origin
     'http://otherdomain.com' has been blocked by CORS policy"

    With this, the browser says: "OK, the API allows it."
    """
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    # Tells browser: cache this CORS check for 10 minutes
    response.headers["Access-Control-Max-Age"] = "600"
    return response


def add_security_headers(response):
    """
    Add basic security headers to every response.
    These are best practices for any web API.
    """
    # Don't let browsers guess the content type
    response.headers["X-Content-Type-Options"] = "nosniff"
    # Don't allow this app to be embedded in an iframe (clickjacking protection)
    response.headers["X-Frame-Options"] = "DENY"
    return response


def apply_all_headers(response):
    """
    Master function — apply ALL headers at once.
    Called in app/main.py after every request.
    """
    response = add_cors_headers(response)
    response = add_security_headers(response)
    return response
