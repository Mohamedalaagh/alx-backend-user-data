#!/usr/bin/env python3
"""Authentication Module.

This module provides the `Auth` class for user authentication,
handling user registration, login, session management, and
password reset functionalities.
"""

import bcrypt
from db import DB
from sqlalchemy.orm.exc import NoResultFound
from typing import Union
from user import User
from uuid import uuid4


def _hash_password(password: str) -> str:
    """Hashes a password with a salt.

    Args:
        password (str): Plain text password to hash.

    Returns:
        str: Salted and hashed password.
    """
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt())


def _generate_uuid() -> str:
    """Generates a new UUID.

    Returns:
        str: String representation of the UUID.
    """
    return str(uuid4())


class Auth:
    """Handles user authentication and interaction with the database."""

    def __init__(self):
        """Initializes the Auth class."""
        self._db = DB()

    def register_user(self, email: str, password: str) -> User:
        """Registers a new user in the database.

        Args:
            email (str): User's email.
            password (str): User's plain text password.

        Returns:
            User: The newly created user object.

        Raises:
            ValueError: If the user with the given email already exists.
        """
        try:
            self._db.find_user_by(email=email)
            raise ValueError(f"User {email} already exists")
        except NoResultFound:
            hashed_password = _hash_password(password)
            return self._db.add_user(email, hashed_password)

    def valid_login(self, email: str, password: str) -> bool:
        """Validates a user's login credentials.

        Args:
            email (str): User's email.
            password (str): User's plain text password.

        Returns:
            bool: True if credentials are valid, False otherwise.
        """
        try:
            user = self._db.find_user_by(email=email)
        except NoResultFound:
            return False

        return bcrypt.checkpw(password.encode(), user.hashed_password)

    def create_session(self, email: str) -> Union[str, None]:
        """Creates a session for the user.

        Args:
            email (str): User's email.

        Returns:
            str | None: Session ID or None if user is not found.
        """
        try:
            user = self._db.find_user_by(email=email)
        except NoResultFound:
            return None

        session_id = _generate_uuid()
        self._db.update_user(user.id, session_id=session_id)
        return session_id

    def get_user_from_session_id(self, session_id: str) -> Union[User, None]:
        """Retrieves a user from their session ID.

        Args:
            session_id (str): Session ID.

        Returns:
            User | None: User object or None if session ID is invalid.
        """
        if not session_id:
            return None
        try:
            return self._db.find_user_by(session_id=session_id)
        except NoResultFound:
            return None

    def destroy_session(self, user_id: int) -> None:
        """Ends a user's session.

        Args:
            user_id (int): User's ID.
        """
        try:
            user = self._db.find_user_by(id=user_id)
        except NoResultFound:
            return
        self._db.update_user(user.id, session_id=None)

    def get_reset_password_token(self, email: str) -> str:
        """Generates a reset password token for the user.

        Args:
            email (str): User's email.

        Returns:
            str: Reset password token.

        Raises:
            ValueError: If user is not found.
        """
        try:
            user = self._db.find_user_by(email=email)
        except NoResultFound:
            raise ValueError

        reset_token = _generate_uuid()
        self._db.update_user(user.id, reset_token=reset_token)
        return reset_token

    def update_password(self, reset_token: str, password: str) -> None:
        """Updates a user's password using a reset token.

        Args:
            reset_token (str): Reset token.
            password (str): New password.

        Raises:
            ValueError: If reset token is invalid or user is not found.
        """
        if not reset_token or not password:
            return

        try:
            user = self._db.find_user_by(reset_token=reset_token)
        except NoResultFound:
            raise ValueError

        hashed_password = _hash_password(password)
        self._db.update_user(user.id, hashed_password=hashed_password, reset_token=None)
