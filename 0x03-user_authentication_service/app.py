#!/usr/bin/env python3
"""
API Routes for Authentication Service
This module provides a Flask-based API for user authentication,
including registration, login, session management, and password
reset functionality.
"""

from auth import Auth
from flask import (
    Flask,
    jsonify,
    request,
    abort,
    redirect
)

app = Flask(__name__)
AUTH = Auth()


@app.route('/', methods=['GET'])
def hello_world() -> str:
    """
    Base route for the authentication service API.
    Returns:
        JSON with a welcome message.
    """
    return jsonify({"message": "Bienvenue"})


@app.route('/users', methods=['POST'])
def register_user() -> str:
    """
    Registers a new user if they do not already exist.
    Request Form:
        - email: User's email address.
        - password: User's password.
    Returns:
        JSON with a success or error message.
    """
    try:
        email = request.form['email']
        password = request.form['password']
    except KeyError:
        abort(400)

    try:
        AUTH.register_user(email, password)
    except ValueError:
        return jsonify({"message": "email already registered"}), 400

    return jsonify({"email": email, "message": "user created"})


@app.route('/sessions', methods=['POST'])
def log_in() -> str:
    """
    Logs in a user and creates a session ID.
    Request Form:
        - email: User's email address.
        - password: User's password.
    Returns:
        JSON with login success message and sets session cookie.
    """
    try:
        email = request.form['email']
        password = request.form['password']
    except KeyError:
        abort(400)

    if not AUTH.valid_login(email, password):
        abort(401)

    session_id = AUTH.create_session(email)
    response = jsonify({"email": email, "message": "logged in"})
    response.set_cookie("session_id", session_id)

    return response


@app.route('/sessions', methods=['DELETE'])
def log_out() -> str:
    """
    Logs out a user by destroying their session.
    Uses session ID from cookies.
    Returns:
        Redirect to the home page if successful, or 403 if invalid.
    """
    session_id = request.cookies.get("session_id")

    if not session_id or not AUTH.get_user_from_session_id(session_id):
        abort(403)

    AUTH.destroy_session(session_id)
    return redirect('/')


@app.route('/profile', methods=['GET'])
def profile() -> str:
    """
    Retrieves the profile of a logged-in user.
    Uses session ID from cookies.
    Returns:
        JSON with the user's email or 403 if invalid session.
    """
    session_id = request.cookies.get("session_id")

    if not session_id:
        abort(403)

    user = AUTH.get_user_from_session_id(session_id)

    if not user:
        abort(403)

    return jsonify({"email": user.email})


@app.route('/reset_password', methods=['POST'])
def reset_password() -> str:
    """
    Generates a reset password token for a registered user.
    Request Form:
        - email: User's email address.
    Returns:
        JSON with the reset token or 403 if email not registered.
    """
    try:
        email = request.form['email']
    except KeyError:
        abort(403)

    try:
        reset_token = AUTH.get_reset_password_token(email)
    except ValueError:
        abort(403)

    return jsonify({"email": email, "reset_token": reset_token})


@app.route('/reset_password', methods=['PUT'])
def update_password() -> str:
    """
    Updates a user's password using a reset token.
    Request Form:
        - email: User's email address.
        - reset_token: Password reset token.
        - new_password: New password for the user.
    Returns:
        JSON with success or error message.
    """
    try:
        email = request.form['email']
        reset_token = request.form['reset_token']
        new_password = request.form['new_password']
    except KeyError:
        abort(400)

    try:
        AUTH.update_password(reset_token, new_password)
    except ValueError:
        abort(403)

    return jsonify({"email": email, "message": "Password updated"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
