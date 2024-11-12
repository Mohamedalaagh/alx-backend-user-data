#!/usr/bin/env python3
"""
API routing module for managing request handling, authentication,
and error responses.

This module:
- Initializes and configures the Flask app.
- Registers routes from `api.v1.views`.
- Applies CORS policy to allow cross-origin requests.
- Integrates an authentication system based on the AUTH_TYPE
  environment variable.
- Defines error handlers for common HTTP errors.
- Implements a request validation hook for secured endpoints.
"""
from os import getenv
from api.v1.views import app_views
from flask import Flask, jsonify, abort, request
from flask_cors import (CORS, cross_origin)

app = Flask(__name__)
app.register_blueprint(app_views)
CORS(app, resources={r"/api/v1/*": {"origins": "*"}})

# Initialize authentication based on AUTH_TYPE environment variable
auth = None
AUTH_TYPE = getenv("AUTH_TYPE")

if AUTH_TYPE == "auth":
    from api.v1.auth.auth import Auth
    auth = Auth()
elif AUTH_TYPE == "basic_auth":
    from api.v1.auth.basic_auth import BasicAuth
    auth = BasicAuth()


@app.errorhandler(404)
def not_found(error) -> str:
    """
    Handles 404 Not Found errors.

    Args:
        error (Exception): The raised exception.
    Returns:
        Response: JSON response with an error message.
    """
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(401)
def unauthorized_error(error) -> str:
    """
    Handles 401 Unauthorized errors.

    Args:
        error (Exception): The raised exception.
    Returns:
        Response: JSON response with an error message.
    """
    return jsonify({"error": "Unauthorized"}), 401


@app.errorhandler(403)
def forbidden_error(error) -> str:
    """
    Handles 403 Forbidden errors.

    Args:
        error (Exception): The raised exception.
    Returns:
        Response: JSON response with an error message.
    """
    return jsonify({"error": "Forbidden"}), 403


@app.before_request
def before_request() -> str:
    """
    Validates incoming requests before routing.

    - Skips validation for excluded paths.
    - Ensures requests include proper authorization headers.
    - Verifies current user identity.
    """
    if auth is None:
        return

    excluded_paths = ['/api/v1/status/',
                      '/api/v1/unauthorized/',
                      '/api/v1/forbidden/']

    if not auth.require_auth(request.path, excluded_paths):
        return

    if auth.authorization_header(request) is None:
        abort(401)

    if auth.current_user(request) is None:
        abort(403)


if __name__ == "__main__":
    """
    Main entry point for the API server.

    - Host and port are configurable via API_HOST and API_PORT
      environment variables.
    - Defaults to host `0.0.0.0` and port `5000`.
    """
    host = getenv("API_HOST", "0.0.0.0")
    port = getenv("API_PORT", "5000")
    app.run(host=host, port=port)
