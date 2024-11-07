#!/usr/bin/env python3
"""
Module for Handling Personal Data

This module provides functionalities for managing personal data securely.
It includes tools for logging with data redaction, connecting to a MySQL
database, and formatting log messages that may contain sensitive
information (PII). This helps ensure that sensitive data like names, emails,
phone numbers, and other PII are protected.

Environment Variables:
    - PERSONAL_DATA_DB_USERNAME: MySQL database username (default: "root").
    - PERSONAL_DATA_DB_PASSWORD: MySQL database password (default: "").
    - PERSONAL_DATA_DB_HOST: MySQL database host (default: "localhost").
    - PERSONAL_DATA_DB_NAME: MySQL database name.
"""

from typing import List
import re
import logging
from os import environ
import mysql.connector


PII_FIELDS = ("name", "email", "phone", "ssn", "password")


def filter_datum(fields: List[str], redaction: str,
                 message: str, separator: str) -> str:
    """
    Obfuscates specified fields in a log message.

    This function takes a list of fields, a redaction string, and a log message
    as input. It then replaces each specified field's value with the redaction
    string, ensuring sensitive data is hidden from log outputs.

    Args:
        fields (List[str]): List of field names to obfuscate in the message.
        redaction (str): The string to replace sensitive information.
        message (str): The log message containing sensitive data.
        separator (str): The character that separates fields in the message.

    Returns:
        str: The obfuscated log message.

    Example:
        >>> filter_datum(["email"], "***", "email=john.doe@example.com;", ";")
        'email=***;'
    """
    for f in fields:
        message = re.sub(f'{f}=.*?{separator}',
                         f'{f}={redaction}{separator}', message)
    return message


def get_logger() -> logging.Logger:
    """
    Creates and configures a Logger for user data.

    The logger is set to the INFO level and is configured with a custom
    formatter that redacts sensitive fields as defined in PII_FIELDS.

    Returns:
        logging.Logger: Configured logger with redaction capabilities.
    """
    logger = logging.getLogger("user_data")
    logger.setLevel(logging.INFO)
    logger.propagate = False

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(RedactingFormatter(list(PII_FIELDS)))
    logger.addHandler(stream_handler)

    return logger


def get_db() -> mysql.connector.connection.MySQLConnection:
    """
    Establishes a connection to the MySQL database using environment variables.

    The database connection parameters are retrieved from environment
    variables with sensible defaults. This function is intended for use in
    a controlled environment where the database contains sensitive information.

    Returns:
        mysql.connector.connection.MySQLConnection:
        A MySQL database connection object.

    Raises:
        mysql.connector.Error: If there's an error connecting to the database.
    """
    username = environ.get("PERSONAL_DATA_DB_USERNAME", "root")
    password = environ.get("PERSONAL_DATA_DB_PASSWORD", "")
    host = environ.get("PERSONAL_DATA_DB_HOST", "localhost")
    db_name = environ.get("PERSONAL_DATA_DB_NAME")

    cnx = mysql.connector.connection.MySQLConnection(user=username,
                                                     password=password,
                                                     host=host,
                                                     database=db_name)
    return cnx


def main():
    """
    Main function that retrieves and logs user data from the database.

    This function connects to the database, retrieves all rows from the 'users'
    table, and logs each row in a redacted format to ensure PII is not exposed.
    It uses a secure logger to handle potentially sensitive data.

    Usage:
        Run this module directly to execute the main function, which outputs
        redacted logs of user data.
    """
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users;")
    field_names = [i[0] for i in cursor.description]

    logger = get_logger()

    for row in cursor:
        str_row = ''.join(f'{f}={str(r)}; ' for r, f in zip(row, field_names))
        logger.info(str_row.strip())

    cursor.close()
    db.close()


class RedactingFormatter(logging.Formatter):
    """
    Custom Formatter that redacts sensitive information in log records.

    This formatter is designed to redact specified PII fields in log messages
    to prevent sensitive information from being exposed in logs.

    Attributes:
        REDACTION (str): Default redaction text.
        FORMAT (str): Log message format.
        SEPARATOR (str): Separator used between fields in log messages.

    Methods:
        format(record): Redacts specified PII fields in the log record.
    """

    REDACTION = "***"
    FORMAT = "[HOLBERTON] %(name)s %(levelname)s %(asctime)-15s: %(message)s"
    SEPARATOR = ";"

    def __init__(self, fields: List[str]):
        """
        Initializes the RedactingFormatter with specific fields to redact.

        Args:
            fields (List[str]): List of field names to redact in log messages.
        """
        super(RedactingFormatter, self).__init__(self.FORMAT)
        self.fields = fields

    def format(self, record: logging.LogRecord) -> str:
        """
        Applies redaction to sensitive fields in the log message.

        Args:
            record (logging.LogRecord): The log record containing the message.

        Returns:
            str: The formatted log message with sensitive fields redacted.
        """
        record.msg = filter_datum(self.fields, self.REDACTION,
                                  record.getMessage(), self.SEPARATOR)
        return super(RedactingFormatter, self).format(record)


if __name__ == '__main__':
    main()
