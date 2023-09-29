import flask_security
from flask import Blueprint, render_template, redirect, url_for, request
from models import CA, Server
from app import db
import uuid
import random
import datetime
from OpenSSL import crypto
import json
from flask_security import login_required
from scripts_lib import *

server_pyopenssl = Blueprint('server_pyopenssl', __name__, template_folder='templates')


@server_pyopenssl.route('/')
@login_required
def index():
    # a = CA.query.filter(CA.id == id).first()
    author = flask_security.current_user.email
    role = flask_security.current_user.roles
    r = role[0].name
    if r == "admin":
        server = Server.query.all()
    else:
        server = Server.query.filter(Server.author == author)

    print(r)
    return render_template('server_pyopenssl/index.html', server=server)
    # return "server_pyopenssl"


@server_pyopenssl.route('/newserver')
@login_required
def newserver():
    date_time_end = (datetime.datetime.now() + datetime.timedelta(days=365)).strftime('%d.%m.%Y %H:%M')
    ca = CA.query.all()
    return render_template('server_pyopenssl/new_server.html', date_time_end=date_time_end, ca=ca)
    # return "newserver"


@server_pyopenssl.route('/create', methods=['POST'])
@login_required
def create():
    # принимаем JSON из формы
    info = request.get_json('name')
    # Совпадение: (-1) - начальное значение, (1) - есть совпадение, (0) - нет совпадения
    coincidence = 0
    # Запрос к БД
    server = Server.query.all()

    # Перебор всех элементов
    for server_item in server:
        if server_item.name == info["name"]:
            coincidence = 1
            break
        elif server_item.name != info["name"]:
            coincidence = 0

    if coincidence == 1:
        data = {"coincidence": coincidence}
        json_data = json.dumps(data)
        # Структура ответа JSON
        # {coincidence (совпадение имени, 0 - нет совпадения, 1 - есть совпадение)}
        # {success (создание ЦС, 0 - ошибка, 1 - успешно)}
        return json_data
    else:
        title = uuid.uuid4().hex
        name = info["name"]
        descr = info["descr"]
        validity = info["validity"] + ':00.000000'
        author = flask_security.current_user.email

        date_time_end = datetime.datetime.strptime(validity, '%d.%m.%Y %H:%M:%S.%f')
        date_time_start = datetime.datetime.now().replace(microsecond=0)
        count_second = int((date_time_end - date_time_start).total_seconds())

        # Содаем пары ключей для сервера
        server_key = crypto.PKey()
        server_key.generate_key(crypto.TYPE_RSA, 2048)

        # Выгружаем из БД сертификат и секретный ключ ЦС
        select_ca = info["select_ca"]
        ca = CA.query.filter(CA.name == select_ca).first()
        key_ca = str.encode(ca.key_ca)
        cert_ca = str.encode(ca.cert_ca)

        # Создаем объект X509 из выгруженного сертификата ЦС
        cert_ca_object = crypto.load_certificate(type=crypto.FILETYPE_PEM, buffer=cert_ca)
        # Создаем объект Pkey из выгруженного секретного ключа ЦС
        key_ca_object = crypto.load_privatekey(type=crypto.FILETYPE_PEM, buffer=key_ca)

        # Создаем сертификат сервера
        server_cert = crypto.X509()
        server_cert.set_version(2)
        server_cert.set_serial_number(random.randint(50000000, 100000000))
        server_subj = server_cert.get_subject()
        server_subj.commonName = title

        # --------------------------------- Добавляем расширения сертификата ЦС ---------------------------------

        server_cert.add_extensions([
            # Расширение: False - является ли расширение критическим; "CA:TRUE" - является ли сертификат корневым ЦС
            crypto.X509Extension("basicConstraints".encode('utf-8'), False, "CA:FALSE".encode('utf-8'))
        ])

        server_cert.add_extensions([
            crypto.X509Extension("subjectKeyIdentifier".encode('utf-8'), False, "hash".encode('utf-8'),
                                 subject=server_cert,
                                 issuer=cert_ca_object)
        ])

        server_cert.add_extensions([
            crypto.X509Extension("authorityKeyIdentifier".encode('utf-8'), False,
                                 "keyid:always, issuer:always".encode('utf-8'), subject=server_cert,
                                 issuer=cert_ca_object)
        ])

        server_cert.add_extensions([
            crypto.X509Extension("extendedKeyUsage".encode('utf-8'), False,
                                 "serverAuth".encode('utf-8'))
        ])

        server_cert.add_extensions([
            crypto.X509Extension("keyUsage".encode('utf-8'), False, "digitalSignature, keyEncipherment".encode('utf-8'))
        ])

        server_cert.add_extensions([
            crypto.X509Extension("subjectAltName".encode('utf-8'), False, ("DNS: " + title).encode('utf-8'))
        ])

        # --------------------------------- Добавляем расширения сертификата ЦС ---------------------------------

        # Получаем информацию о субъекте ЦС из X509
        ca_subj = cert_ca_object.get_subject()

        # Пишем в сертификат сервера информацию и о том кто его выпустил, публичный ключ сервера и подписываем его мекретным ключом ЦС
        server_cert.set_issuer(ca_subj)
        server_cert.set_pubkey(server_key)
        server_cert.sign(key_ca_object, 'sha256')

        # Устанавливаем срок действия сертификата
        server_cert.gmtime_adj_notBefore(0)
        server_cert.gmtime_adj_notAfter(count_second)

        # Вывод содержимого сертификата и секретного ключа сервера
        cert = (crypto.dump_certificate(crypto.FILETYPE_PEM, server_cert))
        key = (crypto.dump_privatekey(crypto.FILETYPE_PEM, server_key))
        cert_decode = cert.decode("utf-8")
        key_decode = key.decode("utf-8")

        print(cert_decode)
        print(key_decode)

        success = 0

        try:
            server = Server(cert_server=cert_decode, key_server=key_decode, title=title, name=name, description=descr,
                            author=author)
            server.ca.append(ca)
            db.session.add(server)
            db.session.commit()
            success = 1
        except:
            print('Error add server')
            success = 0

        data = {"coincidence": coincidence, "success": success}
        json_data = json.dumps(data)
        return json_data

    print(count_second)


@server_pyopenssl.route('/delete/<int:id>')
@login_required
def delete(id):
    print(id)
    a = Server.query.filter(Server.id == id).first()
    for item in a.client:
        db.session.delete(item)

    db.session.delete(a)

    db.session.commit()

    return redirect(url_for('server_pyopenssl.index'))


# Функция запуска сервера
@server_pyopenssl.route('/runServer', methods=['POST'])
@login_required
def runServer():
    # принимаем JSON из формы
    info = request.get_json()
    id = info["id"]
    action = info["action"]

    server = Server.query.filter(Server.id == id).first()
    server_title = server.title

    if action == "start":
        # ---------------Выгружаем из БД сертификат ЦС, которым был подписан сервер ---------------

        # print(server_title)
        ca = server.ca.first()
        cert_ca = str.encode(ca.cert_ca)
        cert_ca_decode = cert_ca.decode("utf-8")
        # ---------------Выгружаем из БД сертификат ЦС, которым был подписан сервер ---------------

        # ---------------Выгружаем из БД сертификат сервера ---------------
        cert_server = str.encode(server.cert_server)
        cert_server_decode = cert_server.decode("utf-8")
        # ---------------Выгружаем из БД сертификат сервера ---------------

        # ---------------Выгружаем из БД ключ сервера ---------------
        key_server = str.encode(server.key_server)
        key_server_decode = key_server.decode("utf-8")
        # ---------------Выгружаем из БД ключ сервера ---------------

        # --------------- Дополнительный ключ ta.key ---------------
        takey = b'-----BEGIN OpenVPN Static key V1-----\n3d6917f1990f8f7fd9d2b0f21275aba2\nf5975b45ac4ac5ca98467fcc5d9c4196\n4a858c21c7b39442ef8802eef571debc\ndc21a9bd3bb4c86c5fbf348413c9d57e\n612a56f6817543a2151f00db8b8eb4b8\nb52c1eb0fc2175e4fa60657adb7a26bb\n976d2b784fed7405cb80daa25bc6cd69\n6d789d266a472acb736dbc9fd6434c81\n40be093408a57674baed234998ef503a\ne8804e5781dbdb4edb02e61fecac418e\nc7196cda225698fa48eb001e48264401\n01c16c381fdf709d32f95bd2f2b18c17\n3b6eb974864cfefa04f9585cb8160288\nfc3ec098674008cd5a2bbe0c866b7a6e\nbc666fd041c62a7498e67bbac5024719\n47fac9db588d631c96184cadd5e5bf0c\n-----END OpenVPN Static key V1-----\n'
        takey_decode = takey.decode("utf-8")
        # --------------- Дополнительный ключ ta.key ---------------

        # --------------- Получаем свободный порт в системе ---------------
        command_freeport = "echo 'PASSWORD' | sudo -S bash success_ports.sh"
        arr_item_freeport = bash(sudo(command_work=command_freeport, password="levashov"))
        # --------------- Получаем свободный порт в системе ---------------

        # Если команда выполнена успешно
        if arr_item_freeport["result"] == 0:
            # --------------- конфигурация сервера ---------------
            a = '\"port ' + arr_item_freeport["stdout"] + '' \
                'proto udp\n' \
                'dev tun\n' \
                '<ca>\n' \
                + cert_ca_decode + \
                '</ca>\n' \
                '<cert>\n' \
                + cert_server_decode + \
                '</cert>\n' \
                '<key>\n' \
                + key_server_decode + \
                '</key>\n' \
                'dh none\n' \
                '<tls-auth>\n' \
                + takey_decode + \
                '</tls-auth>\n' \
                'cipher AES-128-CBC\n' \
                'auth SHA256\n' \
                'server 10.0.0.0 255.255.255.0\n' \
                'keepalive 10 120\n' \
                'persist-key\n' \
                'persist-tun\n' \
                'status server-status.log\n' \
                'log /var/log/server.log\n' \
                'comp-lzo\n' \
                'verb 3\n' \
                'sndbuf 0\n' \
                'rcvbuf 0\n' \
                '\"'
            # --------------- конфигурация сервера ---------------

            command_work = "printf " + a + " > " + server_title + ".conf"
            command_work2 = "echo 'PASSWORD' | sudo -S mv " + server_title + ".conf /etc/openvpn/"
            # command_work = "printf " + a + " > " + "server3" + ".conf"
            # command_work2 = "echo 'PASSWORD' | sudo -S mv " + "server3" + ".conf /etc/openvpn/"
            arr_item_make = bash(sudo(command_work=command_work, password="levashov"))
            arr_item_make2 = bash(sudo(command_work=command_work2, password="levashov"))

            # --------------- запуск сервера ---------------
            command_startserver = "echo 'PASSWORD' | sudo -S systemctl start openvpn@" + server_title
            arr_item_startserver = bash(sudo(command_work=command_startserver, password="levashov"))
            # --------------- запуск сервера ---------------

            # --------------- проверяем статус сервера ---------------
            command_statusserver = "echo 'PASSWORD' | sudo -S systemctl status openvpn@" + server_title
            arr_item_statusserver = bash(sudo(command_work=command_statusserver, password="levashov"))

            check_status = arr_item_statusserver["stdout"].find("active (running)")
            if check_status == -1:
                command_removeserver = "echo 'PASSWORD' | sudo -S rm /etc/openvpn/" + server_title + ".conf"
                arr_item_removeserver = bash(sudo(command_work=command_removeserver, password="levashov"))
            else:
                print("yes")
            # --------------- проверяем статус сервера ---------------

            return arr_item_make2
        else:
            return "Ошибка назначания порта"
    else:
        # --------------- останов сервера ---------------
        command_stopserver = "echo 'PASSWORD' | sudo -S systemctl stop openvpn@" + server_title
        arr_item_stopserver = bash(sudo(command_work=command_stopserver, password="levashov"))
        # --------------- останов сервера ---------------

        # --------------- удаляем временную конфигурацию сервера ---------------
        command_removeserver = "echo 'PASSWORD' | sudo -S rm /etc/openvpn/" + server_title + ".conf"
        arr_item_removeserver = bash(sudo(command_work=command_removeserver, password="levashov"))
        # --------------- удаляем временную конфигурацию сервера ---------------




# @server_pyopenssl.route('/create')
# def create():
#
#     # Получаем данные из формы ввода
#     title = uuid.uuid4().hex
#     name = request.args.get('name')
#     descr = request.args.get('descr')
#     validity = request.args.get('validity') + ':00.000000'
#
#     date_time_end = datetime.datetime.strptime(validity, '%d.%m.%Y %H:%M:%S.%f')
#     date_time_start = datetime.datetime.now().replace(microsecond=0)
#     count_second = int((date_time_end - date_time_start).total_seconds())
#
#     # Содаем пары ключей для сервера
#     server_key = crypto.PKey()
#     server_key.generate_key(crypto.TYPE_RSA, 2048)
#
#     # Выгружаем из БД сертификат и секретный ключ ЦС
#     select_ca = request.args.get('select_ca')
#     ca = CA.query.filter(CA.name == select_ca).first()
#     key_ca = str.encode(ca.key_ca)
#     cert_ca = str.encode(ca.cert_ca)
#
#     # Создаем объект X509 из выгруженного сертификата ЦС
#     cert_ca_object = crypto.load_certificate(type=crypto.FILETYPE_PEM, buffer=cert_ca)
#     # Создаем объект Pkey из выгруженного секретного ключа ЦС
#     key_ca_object = crypto.load_privatekey(type=crypto.FILETYPE_PEM, buffer=key_ca)
#
#     # Создаем сертификат сервера
#     server_cert = crypto.X509()
#     server_cert.set_version(2)
#     server_cert.set_serial_number(random.randint(50000000, 100000000))
#     server_subj = server_cert.get_subject()
#     server_subj.commonName = title
#
#     # --------------------------------- Добавляем расширения сертификата ЦС ---------------------------------
#
#     server_cert.add_extensions([
#         # Расширение: False - является ли расширение критическим; "CA:TRUE" - является ли сертификат корневым ЦС
#         crypto.X509Extension("basicConstraints".encode('utf-8'), False, "CA:FALSE".encode('utf-8'))
#     ])
#
#     server_cert.add_extensions([
#         crypto.X509Extension("subjectKeyIdentifier".encode('utf-8'), False, "hash".encode('utf-8'), subject=server_cert,
#                              issuer=cert_ca_object)
#     ])
#
#     server_cert.add_extensions([
#         crypto.X509Extension("authorityKeyIdentifier".encode('utf-8'), False,
#                              "keyid:always, issuer:always".encode('utf-8'), subject=server_cert, issuer=cert_ca_object)
#     ])
#
#     server_cert.add_extensions([
#         crypto.X509Extension("extendedKeyUsage".encode('utf-8'), False,
#                              "serverAuth".encode('utf-8'))
#     ])
#
#     server_cert.add_extensions([
#         crypto.X509Extension("keyUsage".encode('utf-8'), False, "digitalSignature, keyEncipherment".encode('utf-8'))
#     ])
#
#     server_cert.add_extensions([
#         crypto.X509Extension("subjectAltName".encode('utf-8'), False, ("DNS: " + title).encode('utf-8'))
#     ])
#
#     # --------------------------------- Добавляем расширения сертификата ЦС ---------------------------------
#
#     # Получаем информацию о субъекте ЦС из X509
#     ca_subj = cert_ca_object.get_subject()
#
#     #Пишем в сертификат сервера информацию и о том кто его выпустил, публичный ключ сервера и подписываем его мекретным ключом ЦС
#     server_cert.set_issuer(ca_subj)
#     server_cert.set_pubkey(server_key)
#     server_cert.sign(key_ca_object, 'sha256')
#
#     # Устанавливаем срок действия сертификата
#     server_cert.gmtime_adj_notBefore(0)
#     server_cert.gmtime_adj_notAfter(count_second)
#
#     # Вывод содержимого сертификата и секретного ключа сервера
#     cert = (crypto.dump_certificate(crypto.FILETYPE_PEM, server_cert))
#     key = (crypto.dump_privatekey(crypto.FILETYPE_PEM, server_key))
#     cert_decode = cert.decode("utf-8")
#     key_decode = key.decode("utf-8")
#
#     print(cert_decode)
#     print(key_decode)
#
#     success = 0
#
#     try:
#         server = Server(cert_server=cert_decode, key_server=key_decode, title=title, name=name, description=descr)
#         server.ca.append(ca)
#         db.session.add(server)
#         db.session.commit()
#         success = 1
#     except:
#         print('Error add ca')
#         success = 0
#
#     return render_template('server_pyopenssl/success.html', success=success)
