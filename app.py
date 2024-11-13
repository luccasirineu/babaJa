import os
from dbm import error

import mysql.connector
from flask import Flask, request, jsonify
from werkzeug.security import check_password_hash

from models.user import User
from werkzeug.utils import secure_filename
from flask_cors import CORS
import pymysql

app = Flask(__name__)
CORS(app, origins=["*"])


# Configuração do banco de dados MySQL
db_config = {
    'host': '137.184.82.206',
    'user': 'user_admin',
    'password': '1910',
    'database': 'mydatabase'
}

def get_db_connection():
    return mysql.connector.connect(**db_config)

@app.route('/signup', methods=['POST'])
def signup():
    data = request.json
    username = data.get('new-username')
    password = data.get('new-password')
    confirm_password = data.get('confirm-password')
    role = data.get('user-role-signup')

    print(f'Username: {username}, Password: {password}, Role: {role}')
    # Verifique se as senhas coincidem
    if password != confirm_password:
        return jsonify({"error": "As senhas não coincidem"}), 400

    if User.create_user(username, password, role):
        return jsonify({"message": "Usuário criado com sucesso"}), 201

    return jsonify({"error": "Usuário já cadastrado"}), 500

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")
    role = data.get("user_role")

    # Conexão com o banco de dados
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor(dictionary=True)

    # Verifica se o usuário existe no banco e traz as informações necessárias
    query = "SELECT * FROM users WHERE username = %s AND role = %s"
    cursor.execute(query, (username, role))
    user = cursor.fetchone()

    cursor.close()
    connection.close()

    if not user:
        return jsonify({"error": "Usuário não encontrado"}), 404

    # Verifica se o hash da senha corresponde e se o papel (role) está correto
    if check_password_hash(user['password'], password) and user['role'] == role:
        if role == "baba":
            # Verifica se a idade está nula no banco
            if user.get('idade') is None:
                # Idade está nula, redireciona para a página de confirmação de dados
                return jsonify({"message": "Confirme seus dados", "redirect": "confirmacao", "username": user['username']}), 200
            else:
                # Idade está preenchida, redireciona para o dashboard da babá
                return jsonify({"message": "Login realizado com sucesso", "redirect": "dashboard", "username": user['username']}), 200
        elif role == "pais":
            # Redireciona pais para a página correta
            return jsonify({"message": "Login realizado com sucesso", "username": user['username']}), 200
    else:
        return jsonify({"error": "Usuário ou senha incorretos"}), 401



@app.route('/api/babas', methods=['GET'])
def get_babas():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("""
        SELECT username as nome, idade, experiencia, estado, cidade, descricao, preco_hora, foto_url, num_celular, email 
        FROM users WHERE role = 'baba'
    """)

    babas = cursor.fetchall()

    # Fechar conexão e cursor
    cursor.close()
    connection.close()

    return jsonify(babas)

@app.route('/api/search_babas', methods=['GET'])
def search_babas():
    name = request.args.get('name', '')  # Obtém o nome a partir dos parâmetros de consulta

    # Conectar ao banco de dados
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    # Consulta para buscar babás com nome semelhante ao fornecido
    query = """
        SELECT username as nome, idade, experiencia, estado, cidade, descricao, preco_hora, foto_url, num_celular, email
        FROM users
        WHERE role = 'baba' AND username LIKE %s
    """
    cursor.execute(query, (f"%{name}%",))
    babas = cursor.fetchall()

    # Fechar a conexão e o cursor
    cursor.close()
    connection.close()

    # Retorna a lista de babás que correspondem ao nome pesquisado ou uma lista vazia
    return jsonify(babas), 200


@app.route('/api/baba/<username>', methods=['GET'])
def get_baba_profile(username):

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    query = """
        SELECT username, idade, experiencia, estado, cidade, descricao, preco_hora, num_celular, email 
        FROM users WHERE username = %s AND role = 'baba'
    """
    cursor.execute(query, (username,))
    baba_profile = cursor.fetchone()

    cursor.close()
    connection.close()

    if baba_profile:
        return jsonify(baba_profile), 200
    else:
        return jsonify({"message": "Perfil não encontrado"}), 404


UPLOAD_FOLDER = 'uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


@app.route('/update_baba', methods=['POST'])
def update_baba():
    connection = None
    cursor = None
    try:
        # Receber os dados como FormData
        data = request.form

        username = data.get('username')
        idade = data.get('idade')
        experiencia = data.get('experiencia')
        estado = data.get('estado')
        cidade = data.get('cidade')
        descricao = data.get('descricao')
        preco = data.get('preco_hora')
        num_celular = data.get('num_celular')
        email = data.get('email')

        # Conectar ao banco de dados
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()

        # Atualizar os dados da babá no banco de dados
        update_query = """
        UPDATE users
        SET idade = %s, experiencia = %s, estado = %s, cidade = %s, descricao = %s, preco_hora = %s, num_celular = %s, email = %s
        WHERE username = %s
        """
        cursor.execute(update_query,
                       (idade, experiencia, estado, cidade, descricao, preco, num_celular, email, username))

        # Commitar a transação
        connection.commit()

    except mysql.connector.Error as err:
        print(f"Erro ao atualizar os dados: {err}")
        return jsonify({"error": f"Erro ao atualizar os dados: {err}"}), 500
    finally:
        # Fechar a conexão e o cursor, se foram criados
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()

    return jsonify({"message": "Dados da babá atualizados com sucesso"}), 200




# Testes para visualizar todos os usuários
@app.route('/users', methods=['GET'])
def get_users():
    users = User.get_all_users()
    if users:
        return jsonify(users), 200
    else:
        return jsonify({"message": "Nenhum usuário encontrado"}), 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=True)

