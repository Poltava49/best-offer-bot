import psycopg
from psycopg import Connection



def connect_to_db() -> Connection:
    conn = psycopg.connect(
        host="localhost",
        port=5430,
        database="parser_bot_db",
        user="admin",
        password="qwerty"
    )
    return conn
