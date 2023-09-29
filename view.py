from app import app, user_datastore, db
from flask import render_template, request, jsonify
from flask_security.utils import hash_password
from models import CA, Server, Client, User, Role
import json


@app.route('/')
def index():
    return render_template('index.html')


# метод возвращает все в JSON формате все имена ЦС, серверов, клиентов для валидации форм при создании новых
@app.route('/load_names', methods=['POST'])
def load_names():
    ca = CA.query.all()
    server = Server.query.all()
    client = Client.query.all()

    # Списки с именами
    ca_list = []
    server_list = []
    client_list = []

    for ca_item in ca:
        ca_list.append(ca_item.name)

    for server_item in server:
        server_list.append(server_item.name)

    for client_item in client:
        client_list.append(client_item.name)

    # Словарь с именами
    dict_names = {'ca_names': ca_list, 'server_names': server_list, 'client_names': client_list}
    data = {"success": -1, "description": "descr"}
    json_data = json.dumps(data)

    print(dict_names)
    return json.dumps(dict_names)



@app.route('/process', methods=['POST'])
def process():

    name = request.form['name']

    if name == 'aaa':
        return jsonify({'a': 'yes'})
    else:
        return jsonify({'b': 'no'})

    #return render_template('index.html')


@app.route('/register', methods=['POST', 'GET'])
def register():

    if request.method == 'POST':
        user = user_datastore.create_user(
            email=request.form.get('email'),
            password=hash_password(request.form.get('password')),
            active=0
        )
        db.session.add(user)

        a = Role.query.filter(Role.name == "user").first()
        user_datastore.add_role_to_user(user, a)
        db.session.commit()

    return render_template('register.html')
