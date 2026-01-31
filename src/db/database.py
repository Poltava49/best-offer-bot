import psycopg2




def connect_to_db():
    conn = psycopg2.connect(
        host="localhost",
        port=5430,
        database="parser_bot_db",
        user="admin",
        password="qwerty"
    )
    return conn

