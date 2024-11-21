#!/usr/bin/env python3
"""Database Module for ORM.

This module provides the `DB` class for database interactions, including
user creation, querying, and updating with SQLAlchemy.
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.orm.exc import NoResultFound
from typing import TypeVar
from user import Base, User


class DB:
    """Handles database operations using SQLAlchemy ORM."""

    def __init__(self):
        """Initializes the database connection and tables."""
        self._engine = create_engine("sqlite:///a.db", echo=False)
        Base.metadata.drop_all(self._engine)  # Clears existing tables
        Base.metadata.create_all(self._engine)  # Creates new tables
        self.__session = None

    @property
    def _session(self):
        """Lazy loads the database session.

        Returns:
            Session: SQLAlchemy session instance.
        """
        if self.__session is None:
            DBSession = sessionmaker(bind=self._engine)
            self.__session = DBSession()
        return self.__session

    def add_user(self, email: str, hashed_password: str) -> User:
        """Adds a new user to the database.

        Args:
            email (str): User's email.
            hashed_password (str): User's hashed password.

        Returns:
            User: The created user instance.
        """
        user = User(email=email, hashed_password=hashed_password)
        self._session.add(user)
        self._session.commit()
        return user

    def find_user_by(self, **kwargs) -> User:
        """Finds a user based on provided criteria.

        Args:
            **kwargs: Key-value pairs for filtering the user.

        Returns:
            User: The first user instance matching the criteria.

        Raises:
            InvalidRequestError: If no filter is provided or if an
                                 invalid column name is used.
            NoResultFound: If no user matches the criteria.
        """
        if not kwargs:
            raise InvalidRequestError

        column_names = User.__table__.columns.keys()
        for key in kwargs.keys():
            if key not in column_names:
                raise InvalidRequestError

        user = self._session.query(User).filter_by(**kwargs).first()

        if user is None:
            raise NoResultFound

        return user

    def update_user(self, user_id: int, **kwargs) -> None:
        """Updates a user's attributes in the database.

        Args:
            user_id (int): ID of the user to update.
            **kwargs: Key-value pairs of attributes to update.

        Raises:
            ValueError: If an invalid column name is used.
        """
        user = self.find_user_by(id=user_id)

        column_names = User.__table__.columns.keys()
        for key in kwargs.keys():
            if key not in column_names:
                raise ValueError

        for key, value in kwargs.items():
            setattr(user, key, value)

        self._session.commit()
