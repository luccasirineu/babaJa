import mysql.connector

def get_db_connection():
    return mysql.connector.connect(
        host="137.184.82.206",
        user="user_admin",
        password="1910",
        database="mydatabase"
    )
