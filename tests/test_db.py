import os
from unittest.mock import MagicMock, patch

import psycopg
import pytest

from src.db.database import connect_to_db
from src.exceptions import DatabaseConnectionError


def test_connect_to_db() -> None:
    """Test database connection."""
    mock_conn = MagicMock()

    with (
        patch(
            "src.db.database.psycopg.connect", return_value=mock_conn
        ) as mock_connect,
        patch.dict(
            os.environ,
            {
                "DB_HOST": "localhost",
                "DB_PORT": "5432",
                "DB_NAME": "test_db",
                "DB_USER": "test_user",
                "DB_PASSWORD": "test_pass",
            },
        ),
    ):
        conn = connect_to_db()

        assert conn == mock_conn
        mock_connect.assert_called_once_with(
            host="localhost",
            port=5432,
            dbname="test_db",
            user="test_user",
            password="test_pass",  # noqa: S106
        )


def test_connect_to_db_error() -> None:
    """Test database connection error handling."""
    with (
        patch(
            "src.db.database.psycopg.connect",
            side_effect=psycopg.Error("Connection failed"),
        ),
        patch.dict(
            os.environ,
            {
                "DB_HOST": "localhost",
                "DB_PORT": "5432",
                "DB_NAME": "test_db",
                "DB_USER": "test_user",
                "DB_PASSWORD": "test_pass",
            },
        ),
        pytest.raises(DatabaseConnectionError),
    ):
        connect_to_db()
