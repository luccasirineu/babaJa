import mysql.connector
from flask import current_app
from config import get_db_connection
from werkzeug.security import generate_password_hash


class User:
    @staticmethod
    def create_user(username, password, role):
        connection = get_db_connection()
        cursor = connection.cursor()
        hashed_password = generate_password_hash(password)

        try:
            cursor.execute(
                "INSERT INTO users (username, password, role) VALUES (%s, %s, %s)",
                (username, hashed_password, role)
            )
            connection.commit()
            return True
        except mysql.connector.Error as err:
            print("Erro ao inserir usuário:", err)
            return False
        finally:
            cursor.close()
            connection.close()

    @staticmethod
    def get_all_users():
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute("SELECT id, username, role FROM users")
            users = cursor.fetchall()
            return users
        except mysql.connector.Error as err:
            print("Erro ao buscar usuários:", err)
            return []
        finally:
            cursor.close()
            connection.close()

    @staticmethod
    def get_user_by_username(username):
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        try:
            connection = mysql.connector.connect(
                host="localhost",  # ajuste conforme necessário
                user="root",
                password="1910",
                database="babaja_db"
            )
            cursor = connection.cursor(dictionary=True)
            query = "SELECT * FROM users WHERE username = %s"
            cursor.execute(query, (username,))
            user_data = cursor.fetchone()

            if user_data:
                # Retorna os dados do usuário, incluindo senha e função
                return {
                    "username": user_data["username"],
                    "password": user_data["password"],  # hash da senha armazenada
                    "role": user_data["role"]
                }
            return None
        except mysql.connector.Error as err:
            print(f"Erro ao conectar ou consultar o banco de dados: {err}")
            return None
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
