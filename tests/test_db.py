import os
from unittest.mock import MagicMock, patch

from src.db.database import connect_to_db


def test_connect_to_db() -> None:
    """Test database connection."""
    mock_conn = MagicMock()

    # Разбиваем длинную строку
    with patch(
            "src.db.database.psycopg.connect",
            return_value=mock_conn
    ) as mock_connect, \
            patch.dict(
                os.environ,
                {
                    "DB_HOST": "localhost",
                    "DB_PORT": "5432",
                    "DB_NAME": "test_db",
                    "DB_USER": "test_user",
                    "DB_PASSWORD": "test_pass",
                },
            ):
        conn = connect_to_db()

        assert conn == mock_conn
        mock_connect.assert_called_once_with(
            host="localhost",
            port=5432,
            dbname="test_db",
            user="test_user",
            password="test_pass", # noqa: S106
        )
