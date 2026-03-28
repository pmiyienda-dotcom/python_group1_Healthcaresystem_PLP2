import mysql.connector


def get_connection(dictionary=False):
    conn = mysql.connector.connect(
        host="mysql-38a16d2a-alustudent-b2fa.c.aivencloud.com",
        port=21798,
        user="avnadmin",
        password="AVNS_ZAY1FDa7o5Dfa7-4QdQ",
        database="first_database",
        ssl_disabled=False,
    )
    _original_cursor = conn.cursor
    conn.cursor = lambda **kwargs: _original_cursor(dictionary=dictionary, **kwargs)
    return conn
