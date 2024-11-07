#!/usr/bin/env python3
"""
Password Encryption and Validation Module

This module provides functionality for securely hashing and
validating passwords
using bcrypt. It includes functions to generate a salted, hashed version of a
password and to validate a plain text password against a stored hashed version.

bcrypt is a hashing algorithm designed specifically for securely storing
passwords. It adds a salt to each password hash, making it more resistant
to brute-force attacks.
"""

import bcrypt


def hash_password(password: str) -> bytes:
    """
    Generates a salted and hashed password.

    This function takes a plain text password, encodes it to bytes, and uses
    bcrypt to create a secure hash. The bcrypt algorithm includes a unique
    salt for each hash, ensuring that even identical passwords will have
    different hashes.

    Args:
        password (str): The plain text password to be hashed.

    Returns:
        bytes: A byte string representing the hashed password with an embedded
               salt, suitable for secure storage.

    Example:
        >>> hashed = hash_password("my_secure_password")
        >>> print(hashed)
        b'$2b$12$...'
    """
    # Encode the password as bytes before hashing
    encoded = password.encode()
    # Generate a hashed password with bcrypt, which includes a salt
    hashed = bcrypt.hashpw(encoded, bcrypt.gensalt())

    return hashed


def is_valid(hashed_password: bytes, password: str) -> bool:
    """
    Validates whether the provided plain text password matches the stored
    hashed password.

    This function checks if a given plain text password, when hashed, matches
    the specified stored hashed password. This is achieved using bcrypt’s
    `checkpw` function, which handles both the hashing and comparison.

    Args:
        hashed_password (bytes): The stored password hash to validate against.
        password (str): The plain text password to validate.

    Returns:
        bool: True if the plain text password matches the hashed password,
              False otherwise.

    Example:
        >>> hashed = hash_password("my_secure_password")
        >>> is_valid(hashed, "my_secure_password")
        True
        >>> is_valid(hashed, "incorrect_password")
        False
    """
    # Encode the plain text password to bytes
    encoded = password.encode()
    # Use bcrypt's checkpw to compare the password and hash
    return bcrypt.checkpw(encoded, hashed_password)
