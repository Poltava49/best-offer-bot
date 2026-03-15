"""Database connection module for PostgreSQL."""

import os

import psycopg
from psycopg import Connection

from src.exceptions import DatabaseConnectionError


def connect_to_db() -> Connection:
    """Connect to database."""
    try:
        return psycopg.connect(
            host=os.getenv("DB_HOST"),
            port=int(os.getenv("DB_PORT", "5432")),
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
        )
    except psycopg.Error as e:
        raise DatabaseConnectionError from e
