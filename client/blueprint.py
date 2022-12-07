from flask import Blueprint, render_template, request
import subprocess
import shutil
import uuid
from models import Clients
from app import db


client = Blueprint('client', __name__, template_folder='templates')


@client.route('/')
def index():
    # clients = Clients.query.all()
    # clients = Clients.query.filter(Clients.id == 2).first()
    return render_template('client/index.html')


@client.route('/createclient')
def createclient():
    title = uuid.uuid4().hex
    command_path = "export PATH=$PATH:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games:/snap/bin; "
    command_work = "cd ~/easy-rsa; echo yes | ./easyrsa gen-req " + title + " nopass; echo yes | ./easyrsa sign-req client " + title
    command = command_path + command_work

    result = subprocess.run(command,\
	stderr=subprocess.PIPE,\
	stdout=subprocess.PIPE,\
	shell=True,\
	encoding='utf-8')
    # содержимое сертификата
    q = open('../easy-rsa/pki/issued/' + title + '.crt', encoding="utf-8")
    f_crt = q.read()
    q.close()
    # содержимое ключа
    q = open('../easy-rsa/pki/private/' + title + '.key', encoding="utf-8")
    f_key = q.read()
    q.close()
    # содержимое симметричного ключа ta.key
    q = open('../easy-rsa/ta.key', encoding="utf-8")
    f_ta = q.read()
    q.close()
    # содержимое сертификата ЦС
    q = open('../easy-rsa/pki/ca.crt', encoding="utf-8")
    f_cert_ca = q.read()
    q.close()

    name = request.args.get('name')
    descr = request.args.get('descr')

    print(descr)

    try:
        client = Clients(title=title, name=name, description=descr, crt=f_crt, key=f_key, ta=f_ta, cert_ca=f_cert_ca)
        db.session.add(client)
        db.session.commit()
    except:
        print('Error add client')


    return render_template('client/success.html', cert_ca=f_cert_ca, crt=f_crt, key=f_key, ta=f_ta)
