import flask_security
from flask import Blueprint, render_template, redirect, url_for, request
from models import CA
from app import db
import uuid
import random
import datetime
from OpenSSL import crypto
import json
from flask_security import login_required

ca_pyopenssl = Blueprint('ca_pyopenssl', __name__, template_folder='templates')


@ca_pyopenssl.route('/')
@login_required
def index():
    ca = CA.query.all()
    return render_template('ca_pyopenssl/index.html', ca=ca)


@ca_pyopenssl.route('/newca')
@login_required
def newca():
    date_time_end = (datetime.datetime.now() + datetime.timedelta(days=3650)).strftime('%d.%m.%Y %H:%M')
    print(date_time_end)
    return render_template('ca_pyopenssl/new_ca.html', date_time_end=date_time_end)


@ca_pyopenssl.route('/show_details/<int:id>')
@login_required
def show_details(id):
    ca = CA.query.filter(CA.id == id).first()
    return render_template('ca_pyopenssl/show_details.html', ca=ca)


@ca_pyopenssl.route('/create', methods=['POST'])
@login_required
def create():
    # принимаем JSON из формы
    info = request.get_json('name')
    # Совпадение: (-1) - начальное значение, (1) - есть совпадение, (0) - нет совпадения
    coincidence = 0
    # Запрос к БД
    ca = CA.query.all()

    # Перебор всех элементов
    for ca_item in ca:
        if ca_item.name == info["name"]:
            coincidence = 1
            break
        elif ca_item.name != info["name"]:
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
        descr  = info["descr"]
        validity = info["validity"] + ':00.000000'
        author = flask_security.current_user.email

        date_time_end = datetime.datetime.strptime(validity, '%d.%m.%Y %H:%M:%S.%f')
        date_time_start = datetime.datetime.now().replace(microsecond=0)
        count_second = int((date_time_end - date_time_start).total_seconds())

        # data = {"coincidence": coincidence, "count_second": count_second}
        # json_data = json.dumps(data)
        # return json_data

        ca_key = crypto.PKey()
        ca_key.generate_key(crypto.TYPE_RSA, 2048)

        ca_cert = crypto.X509()
        ca_cert.set_version(2)
        ca_cert.set_serial_number(random.randint(50000000, 100000000))

        ca_subj = ca_cert.get_subject()
        ca_subj.commonName = title

        # --------------------------------- Добавляем расширения сертификата ЦС ---------------------------------

        ca_cert.add_extensions([
            crypto.X509Extension("subjectKeyIdentifier".encode('utf-8'), False, "hash".encode('utf-8'), subject=ca_cert, issuer=ca_cert)
        ])

        ca_cert.add_extensions([
            crypto.X509Extension("authorityKeyIdentifier".encode('utf-8'), False, "keyid:always, issuer:always".encode('utf-8'), subject=ca_cert, issuer=ca_cert)
        ])

        ca_cert.add_extensions([
            # Расширение: False - является ли расширение критическим; "CA:TRUE" - является ли сертификат корневым ЦС
               crypto.X509Extension("basicConstraints".encode('utf-8'), False, "CA:TRUE".encode('utf-8')),
            crypto.X509Extension("keyUsage".encode('utf-8'), False, "keyCertSign, cRLSign".encode('utf-8'))
        ])
        # --------------------------------- Добавляем расширения сертификата ЦС ---------------------------------

        ca_cert.set_issuer(ca_subj)
        ca_cert.set_pubkey(ca_key)
        ca_cert.sign(ca_key, 'sha256')

        ca_cert.gmtime_adj_notBefore(0)
        ca_cert.gmtime_adj_notAfter(count_second)

        cert = (crypto.dump_certificate(crypto.FILETYPE_PEM, ca_cert))
        key = (crypto.dump_privatekey(crypto.FILETYPE_PEM, ca_key))
        cert_decode = cert.decode("utf-8")
        key_decode = key.decode("utf-8")
        print(key)

        cert_asn1 = (crypto.dump_certificate(crypto.FILETYPE_ASN1, ca_cert))
        key_asn1 = (crypto.dump_privatekey(crypto.FILETYPE_ASN1, ca_key))
        # cert_asn1_decode = cert_asn1.decode("utf-8")
        # key_asn1_decode = key_asn1.decode("utf-8")
        print(cert_asn1)
        print(key_asn1)

        success = 0

        try:
            ca = CA(title=title, cert_ca=cert_decode, key_ca=key_decode, name=name, description=descr, author=author)
            db.session.add(ca)
            db.session.commit()
            success = 1
        except:
            print('Error add ca')
            success = 0

        data = {"coincidence": coincidence, "success": success}
        json_data = json.dumps(data)
        return json_data









# @ca_pyopenssl.route('/create')
# def create():
#     title       = uuid.uuid4().hex
#     name        = request.args.get('name')
#     descr       = request.args.get('descr')
#     validity    = request.args.get('validity') + ':00.000000'
#
#     date_time_end = datetime.datetime.strptime(validity, '%d.%m.%Y %H:%M:%S.%f')
#     date_time_start = datetime.datetime.now().replace(microsecond=0)
#     count_second = int((date_time_end - date_time_start).total_seconds())
#
#     ca_key = crypto.PKey()
#     ca_key.generate_key(crypto.TYPE_RSA, 2048)
#
#     ca_cert = crypto.X509()
#     ca_cert.set_version(2)
#     ca_cert.set_serial_number(random.randint(50000000, 100000000))
#
#     ca_subj = ca_cert.get_subject()
#     ca_subj.commonName = title
#
#     # --------------------------------- Добавляем расширения сертификата ЦС ---------------------------------
#
#     ca_cert.add_extensions([
#         crypto.X509Extension("subjectKeyIdentifier".encode('utf-8'), False, "hash".encode('utf-8'), subject=ca_cert, issuer=ca_cert)
#     ])
#
#     ca_cert.add_extensions([
#         crypto.X509Extension("authorityKeyIdentifier".encode('utf-8'), False, "keyid:always, issuer:always".encode('utf-8'), subject=ca_cert, issuer=ca_cert)
#     ])
#
#     ca_cert.add_extensions([
#         # Расширение: False - является ли расширение критическим; "CA:TRUE" - является ли сертификат корневым ЦС
#         crypto.X509Extension("basicConstraints".encode('utf-8'), False, "CA:TRUE".encode('utf-8')),
#         crypto.X509Extension("keyUsage".encode('utf-8'), False, "keyCertSign, cRLSign".encode('utf-8'))
#     ])
#     # --------------------------------- Добавляем расширения сертификата ЦС ---------------------------------
#
#     ca_cert.set_issuer(ca_subj)
#     ca_cert.set_pubkey(ca_key)
#     ca_cert.sign(ca_key, 'sha256')
#
#     ca_cert.gmtime_adj_notBefore(0)
#     ca_cert.gmtime_adj_notAfter(count_second)
#
#     cert = (crypto.dump_certificate(crypto.FILETYPE_PEM, ca_cert))
#     key = (crypto.dump_privatekey(crypto.FILETYPE_PEM, ca_key))
#     cert_decode = cert.decode("utf-8")
#     key_decode = key.decode("utf-8")
#     print(key)
#
#     cert_asn1 = (crypto.dump_certificate(crypto.FILETYPE_ASN1, ca_cert))
#     key_asn1 = (crypto.dump_privatekey(crypto.FILETYPE_ASN1, ca_key))
#     # cert_asn1_decode = cert_asn1.decode("utf-8")
#     # key_asn1_decode = key_asn1.decode("utf-8")
#     print(cert_asn1)
#     print(key_asn1)
#
#     success = 0
#
#     try:
#         ca = CA(title=title, cert_ca=cert_decode, key_ca=key_decode, name=name, description=descr)
#         db.session.add(ca)
#         db.session.commit()
#         success = 1
#     except:
#         print('Error add ca')
#         success = 0
#
#     return render_template('ca_pyopenssl/success.html', success=success)


@ca_pyopenssl.route('/delete/<int:id>')
@login_required
def delete(id):
    a = CA.query.filter(CA.id == id).first()
    for item in a.server:
        for client_item in item.client:
            db.session.delete(client_item)
        db.session.delete(item)

    db.session.delete(a)

    db.session.commit()

    return redirect(url_for('ca_pyopenssl.index'))
