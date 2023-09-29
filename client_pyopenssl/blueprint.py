import flask_security
from flask import Blueprint, render_template, redirect, url_for, request, flash, send_file
from models import CA, Server, Client
from app import db
import uuid
import random
import datetime
from OpenSSL import crypto
import json
from flask_security import login_required
import io, csv

client_pyopenssl = Blueprint('client_pyopenssl', __name__, template_folder='templates')


@client_pyopenssl.route('/download')
def download():
    a = "client\n" \
        "dev tun\n" \
        "proto udp\n" \
        "remote 81.163.30.237 1194\n" \
        "resolv-retry infinite\n" \
        "nobind\n" \
        "persist-key\n" \
        "persist-tun\n" \
        ""
    row = [a]
    proxy = io.StringIO()
    writer = csv.writer(proxy)
    writer.writerow(row)
    # Creating the byteIO object from the StringIO Object
    mem = io.BytesIO()
    # mem.write(proxy.getvalue().encode())
    m = proxy.getvalue().encode()
    m = m.replace(b'"', b'')
    mem.write(m)
    print(m)
    # seeking was necessary. Python 3.5.2, Flask 0.12.2  b = b.replace(b'\x00', b'')
    mem.seek(0)
    proxy.close()

    return send_file(
        mem,
        as_attachment=True,
        download_name='test.csv',
        mimetype='text/csv'
    )



@client_pyopenssl.route('/')
@login_required
def index():
    author = flask_security.current_user.email
    role = flask_security.current_user.roles
    r = role[0].name
    print(r)
    if r == "admin":
        client = Client.query.all()
    else:
        client = Client.query.filter(Client.author == author)

    return render_template('client_pyopenssl/index.html', client=client)


@client_pyopenssl.route('/newclient')
@login_required
def newclient():
    author = flask_security.current_user.email
    role = flask_security.current_user.roles
    r = role[0].name
    if r == "admin":
        server = Server.query.all()
    else:
        server = Server.query.filter(Server.author == author)
    print(r)
    date_time_end = (datetime.datetime.now() + datetime.timedelta(days=30)).strftime('%d.%m.%Y %H:%M')
    # server = Server.query.all()
    return render_template('client_pyopenssl/new_client.html', date_time_end=date_time_end, server=server)
    #return "newclient"


@client_pyopenssl.route('/create', methods=["POST"])
@login_required
def create():
    # принимаем JSON из формы
    info = request.get_json('name')
    # Совпадение: (-1) - начальное значение, (1) - есть совпадение, (0) - нет совпадения
    coincidence = 0
    # Запрос к БД
    client = Client.query.all()

    # Перебор всех элементов
    for client_item in client:
        if client_item.name == info["name"]:
            coincidence = 1
            break
        elif client_item.name != info["name"]:
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
        client_key = crypto.PKey()
        client_key.generate_key(crypto.TYPE_RSA, 2048)

        # Выгружаем из БД сертификат и секретный ключ ЦС
        select_server = info["select_server"]
        server = Server.query.filter(Server.name == select_server).first()
        ca = server.ca.first()
        key_ca = str.encode(ca.key_ca)
        cert_ca = str.encode(ca.cert_ca)

        # Создаем объект X509 из выгруженного сертификата ЦС
        cert_ca_object = crypto.load_certificate(type=crypto.FILETYPE_PEM, buffer=cert_ca)
        # Создаем объект Pkey из выгруженного секретного ключа ЦС
        key_ca_object = crypto.load_privatekey(type=crypto.FILETYPE_PEM, buffer=key_ca)

        # Создаем сертификат клиента
        client_cert = crypto.X509()
        client_cert.set_version(2)
        client_cert.set_serial_number(random.randint(50000000, 100000000))
        client_subj = client_cert.get_subject()
        client_subj.commonName = title

        # --------------------------------- Добавляем расширения сертификата ЦС ---------------------------------

        client_cert.add_extensions([
            # Расширение: False - является ли расширение критическим; "CA:TRUE" - является ли сертификат корневым ЦС
            crypto.X509Extension("basicConstraints".encode('utf-8'), False, "CA:FALSE".encode('utf-8'))
        ])

        client_cert.add_extensions([
            crypto.X509Extension("subjectKeyIdentifier".encode('utf-8'), False, "hash".encode('utf-8'),
                                 subject=client_cert,
                                 issuer=cert_ca_object)
        ])

        client_cert.add_extensions([
            crypto.X509Extension("authorityKeyIdentifier".encode('utf-8'), False,
                                 "keyid:always, issuer:always".encode('utf-8'), subject=client_cert,
                                 issuer=cert_ca_object)
        ])

        client_cert.add_extensions([
            crypto.X509Extension("extendedKeyUsage".encode('utf-8'), False,
                                 "clientAuth".encode('utf-8'))
        ])

        client_cert.add_extensions([
            crypto.X509Extension("keyUsage".encode('utf-8'), False, "digitalSignature".encode('utf-8'))
        ])

        # --------------------------------- Добавляем расширения сертификата ЦС ---------------------------------

        # Получаем информацию о субъекте ЦС из X509
        ca_subj = cert_ca_object.get_subject()

        # Пишем в сертификат клиента информацию и о том кто его выпустил, публичный ключ клиента и подписываем его секретным ключом ЦС
        client_cert.set_issuer(ca_subj)
        client_cert.set_pubkey(client_key)
        client_cert.sign(key_ca_object, 'sha256')

        # Устанавливаем срок действия сертификата
        client_cert.gmtime_adj_notBefore(0)
        client_cert.gmtime_adj_notAfter(count_second)

        # Вывод содержимого сертификата и секретного ключа клиента
        cert = (crypto.dump_certificate(crypto.FILETYPE_PEM, client_cert))
        key = (crypto.dump_privatekey(crypto.FILETYPE_PEM, client_key))
        cert_decode = cert.decode("utf-8")
        key_decode = key.decode("utf-8")

        print(cert_decode)
        print(key_decode)

        success = 0

        try:
            client = Client(cert_client=cert_decode, key_client=key_decode, title=title, name=name, description=descr, author=author)
            client.server.append(server)
            db.session.add(client)
            db.session.commit()
            success = 1
        except:
            print('Error add client')
            success = 0

        data = {"coincidence": coincidence, "success": success}
        json_data = json.dumps(data)
        return json_data


@client_pyopenssl.route('/delete/<int:id>')
@login_required
def delete(id):
    print(id)
    a = Client.query.filter(Client.id == id).first()

    db.session.delete(a)

    db.session.commit()

    return redirect(url_for('client_pyopenssl.index'))


# @client_pyopenssl.route('/create', methods=["POST"])
# def create():
#     if request.method == 'POST':
#         # Получаем данные из формы ввода
#         title = uuid.uuid4().hex
#         name = request.args.get('name')
#         descr = request.args.get('descr')
#         validity = request.args.get('validity') + ':00.000000'
#         select_server = request.form['select_server']
#
#         flash_list = []
#         flash_list.append(name)
#
#         flash(flash_list)
#
#
#         # Находим ЦС, которым подписан сервер
#
#         # date_time_end = datetime.datetime.strptime(validity, '%d.%m.%Y %H:%M:%S.%f')
#         # date_time_start = datetime.datetime.now().replace(microsecond=0)
#         # count_second = int((date_time_end - date_time_start).total_seconds())
#         #
#         #return select_server
#         return render_template('client_pyopenssl/new_client.html')