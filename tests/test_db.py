from src.db.database import connect_to_db

import pytest
import os
from unittest.mock import patch, MagicMock


def test_connect_to_db():
    mock_conn = MagicMock()

    with patch('psycopg.connect', return_value=mock_conn) as mock_connect:
        with patch.dict(os.environ, {
            "DB_HOST": "localhost",
            "DB_PORT": "5432",
            "DB_NAME": "test_db",
            "DB_USER": "test_user",
            "DB_PASSWORD": "test_pass"
        }):
            conn = connect_to_db()
            assert conn == mock_conn
            mock_connect.assert_called_once_with(
                host="localhost",
                port=5432,
                dbname="test_db",
                user="test_user",
                password="test_pass"
            )
