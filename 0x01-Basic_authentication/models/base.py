#!/usr/bin/env python3
"""
Base module for managing generic object persistence and operations.

This module defines:
- The `Base` class, which provides:
  - Initialization with unique IDs and timestamps.
  - Serialization and deserialization of objects.
  - File-based storage and retrieval.
  - Support for CRUD operations (Create, Read, Update, Delete).
  - Searching and counting objects.

Global Constants:
- `TIMESTAMP_FORMAT`: Defines the datetime format for serialization.
- `DATA`: In-memory storage for objects by class name.
"""
from datetime import datetime
from typing import TypeVar, List, Iterable
from os import path
import json
import uuid

TIMESTAMP_FORMAT = "%Y-%m-%dT%H:%M:%S"
DATA = {}


class Base:
    """
    A base class to provide common functionality for object management.

    Attributes:
        id (str): Unique identifier for the object.
        created_at (datetime): Timestamp of creation.
        updated_at (datetime): Timestamp of the last update.
    """

    def __init__(self, *args: list, **kwargs: dict):
        """
        Initialize a `Base` instance with optional attributes.

        Args:
            *args (list): Positional arguments (not used).
            **kwargs (dict): Dictionary of attributes for initialization.
        """
        s_class = str(self.__class__.__name__)
        if DATA.get(s_class) is None:
            DATA[s_class] = {}

        self.id = kwargs.get('id', str(uuid.uuid4()))
        self.created_at = datetime.strptime(
            kwargs.get('created_at'), TIMESTAMP_FORMAT
        ) if kwargs.get('created_at') else datetime.utcnow()
        self.updated_at = datetime.strptime(
            kwargs.get('updated_at'), TIMESTAMP_FORMAT
        ) if kwargs.get('updated_at') else datetime.utcnow()

    def __eq__(self, other: TypeVar('Base')) -> bool:
        """
        Compare equality between two `Base` objects.

        Args:
            other (Base): The other object to compare.
        Returns:
            bool: True if objects are equal, False otherwise.
        """
        return isinstance(other, Base) and self.id == other.id

    def to_json(self, for_serialization: bool = False) -> dict:
        """
        Convert the object to a JSON-compatible dictionary.

        Args:
            for_serialization (bool): Include all attributes if True.
        Returns:
            dict: JSON-compatible representation of the object.
        """
        result = {}
        for key, value in self.__dict__.items():
            if not for_serialization and key.startswith('_'):
                continue
            result[key] = value.strftime(
                TIMESTAMP_FORMAT
            ) if isinstance(value, datetime) else value
        return result

    @classmethod
    def load_from_file(cls):
        """
        Load all objects of the class from a JSON file.
        """
        s_class = cls.__name__
        file_path = f".db_{s_class}.json"
        DATA[s_class] = {}
        if not path.exists(file_path):
            return

        with open(file_path, 'r') as f:
            objs_json = json.load(f)
            for obj_id, obj_json in objs_json.items():
                DATA[s_class][obj_id] = cls(**obj_json)

    @classmethod
    def save_to_file(cls):
        """
        Save all objects of the class to a JSON file.
        """
        s_class = cls.__name__
        file_path = f".db_{s_class}.json"
        objs_json = {obj_id: obj.to_json(True)
                     for obj_id, obj in DATA[s_class].items()}

        with open(file_path, 'w') as f:
            json.dump(objs_json, f)

    def save(self):
        """
        Save the current object to in-memory storage and file.
        """
        s_class = self.__class__.__name__
        self.updated_at = datetime.utcnow()
        DATA[s_class][self.id] = self
        self.__class__.save_to_file()

    def remove(self):
        """
        Remove the object from in-memory storage and file.
        """
        s_class = self.__class__.__name__
        if DATA[s_class].get(self.id):
            del DATA[s_class][self.id]
            self.__class__.save_to_file()

    @classmethod
    def count(cls) -> int:
        """
        Count all objects of the class.

        Returns:
            int: Number of objects.
        """
        return len(DATA[cls.__name__])

    @classmethod
    def all(cls) -> Iterable[TypeVar('Base')]:
        """
        Retrieve all objects of the class.

        Returns:
            Iterable[Base]: All objects of the class.
        """
        return cls.search()

    @classmethod
    def get(cls, id: str) -> TypeVar('Base'):
        """
        Retrieve an object by its ID.

        Args:
            id (str): The object's unique ID.
        Returns:
            Base: The object, or None if not found.
        """
        return DATA[cls.__name__].get(id)

    @classmethod
    def search(cls, attributes: dict = {}) -> List[TypeVar('Base')]:
        """
        Search for objects with matching attributes.

        Args:
            attributes (dict): Attributes to match.
        Returns:
            List[Base]: List of matching objects.
        """
        def _search(obj):
            return all(
                getattr(obj, k, None) == v
                for k, v in attributes.items()
            )

        return list(filter(_search, DATA[cls.__name__].values()))
