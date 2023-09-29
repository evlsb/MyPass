from flask import Blueprint, render_template, request
from models import User, Role
from app import db
import json

users = Blueprint('users', __name__, template_folder='templates')


@users.route('/')
def index():
    # Формируем словарь ролей и клиентов
    roles = Role.query.all()
    d_users = {}
    d_users1 = {}

    for role_item in roles:
        role_name = role_item.name
        a = role_item.users
        dic_email = {}
        for i in a:
            dic_email[i.email] = i.active
        d_users1[role_name] = dic_email
    print(d_users1)

    for role_item in roles:
        role_name = role_item.name
        a = role_item.users
        list_email = []
        for i in a:
            list_email.append(i.email)
        d_users[role_name] = list_email
    print(d_users)

    return render_template('users/index.html', d_users=d_users, d_users1=d_users1)


@users.route('/del_users', methods=['POST'])
def del_users():
    # принимаем JSON из формы
    info = request.get_json("name")
    name = info["name"]
    print(info["name"])

    success = 0
    try:
        User.query.filter(User.email == info['name']).delete()
        db.session.commit()
        success = 1
    except:
        success = 0

    data = {"success": success, "name": name}
    json_data = json.dumps(data)
    return json_data


@users.route('/activate', methods=['POST'])
def activate():
    # принимаем JSON из формы
    info = request.get_json('name')
    name = info['name']
    active = 0
    success = 0
    print(info['name'])
    try:
        admin = User.query.filter_by(email=name).first()
        if admin.active:
            admin.active = 0
            active = admin.active
        else:
            admin.active = 1
            active = admin.active

        db.session.commit()
        success = 1
    except:
        success = 0

    # print(active)
    # admin.email = 'my_new_email@example.com'
    # db.session.commit()

    data = {"success": success, "active": active}
    json_data = json.dumps(data)
    return json_data
