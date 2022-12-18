from flask import Blueprint, render_template, request
import subprocess, sys
import shlex
import shutil
import uuid
from models import Clients
from app import db

server = Blueprint('server', __name__, template_folder='templates')


@server.route('/initpki')
def initpki():
    command_path = "export PATH=$PATH:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr" \
                   "/local/games:/snap/bin; "
    command_work = "cd ~/easy-rsa/; ./easyrsa init-pki"
    command = command_path + command_work
    result = subprocess.run(command, \
                            stderr=subprocess.PIPE, \
                            stdout=subprocess.PIPE, \
                            shell=True, \
                            encoding='utf-8')
    return render_template('server/index.html', er=result.stderr, out=result.stdout, ret=result.returncode)


@server.route('/createclient')
def createclient():
    title = uuid.uuid4().hex
    command_path = "export PATH=$PATH:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games:/snap/bin; "
    command_work = "cd ~/easy-rsa; echo yes | ./easyrsa gen-req " + title + " nopass; echo yes | ./easyrsa sign-req client " + title
    command = command_path + command_work

    result = subprocess.run(command, \
                            stderr=subprocess.PIPE, \
                            stdout=subprocess.PIPE, \
                            shell=True, \
                            encoding='utf-8')

    # содержимое сертификата
    # q = open('../easy-rsa/pki/issued/' + title + '.crt', encoding="utf-8")
    # f_crt = q.read()
    # q.close()
    # содержимое ключа
    # q = open('../easy-rsa/pki/private/' + title + '.key', encoding="utf-8")
    # f_key = q.read()
    # q.close()
    # содержимое симметричного ключа ta.key
    # q = open('../easy-rsa/ta.key', encoding="utf-8")
    # f_ta = q.read()
    # q.close()
    # содержимое сертификата ЦС
    # q = open('../easy-rsa/pki/ca.crt', encoding="utf-8")
    # f_cert_ca = q.read()
    # q.close()

    # name = request.args.get('name')
    # descr = request.args.get('descr')

    # print(descr)

    # try:
    #   client = Clients(title=title, name=name, description=descr, crt=f_crt, key=f_key, ta=f_ta, cert_ca=f_cert_ca)
    #  db.session.add(client)
    # db.session.commit()
    # except:
    #   print('Error add client')

    return render_template('server/index.html')


@server.route('/createta')
def createta():
    command_path = "export PATH=$PATH:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games:/snap/bin; "
    command_work = "cd ~/easy-rsa; echo yes | openvpn --genkey --secret ta.key"
    command = command_path + command_work

    result = subprocess.run(command, \
                            stderr=subprocess.PIPE, \
                            stdout=subprocess.PIPE, \
                            shell=True, \
                            encoding='utf-8')

    # содержимое сертификата
    q = open('../easy-rsa/pki/issued/server.crt', encoding="utf-8")
    f_crt = q.read()
    q.close()
    # содержимое ключа
    q = open('../easy-rsa/pki/private/server.key', encoding="utf-8")
    f_key = q.read()
    q.close()

    return render_template('server/index.html')


@server.route('/createserver')
def createserver():
    stri = 'set_var EASYRSA_ALGO "ec"\nset_var EASYRSA_DIGEST "sha512"'

    file = open("vars", "w+")
    file.write(stri)
    file.close()

    shutil.move("vars", "../easy-rsa")

    command_path = "export PATH=$PATH:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games:/snap/bin; "
    command_work = "cd ~/easy-rsa; echo yes | ./easyrsa gen-req server nopass; echo yes | ./easyrsa sign-req server server"
    command = command_path + command_work
    result = subprocess.run(command, \
                            stderr=subprocess.PIPE, \
                            stdout=subprocess.PIPE, \
                            shell=True, \
                            encoding='utf-8')

    command_work = "cd ~/easy-rsa; rm vars"
    command = command_path + command_work
    result = subprocess.run(command, \
                            stderr=subprocess.PIPE, \
                            stdout=subprocess.PIPE, \
                            shell=True, \
                            encoding='utf-8')

    return render_template('server/index.html')


@server.route('/createca')
def createca():
    country = request.args.post('country')
    province = request.args.get('province')
    city = request.args.get('city')
    org = request.args.get('org')
    email = request.args.get('email')
    ou = request.args.get('ou')

    stri = 'set_var EASYRSA_REQ_COUNTRY    "' + str(country) + '"\n' + \
           'set_var EASYRSA_REQ_PROVINCE   "' + str(province) + '"\n' + \
           'set_var EASYRSA_REQ_CITY       "' + str(city) + '"\n' + \
           'set_var EASYRSA_REQ_ORG        "' + str(org) + '"\n' + \
           'set_var EASYRSA_REQ_EMAIL      "' + str(email) + '"\n' + \
           'set_var EASYRSA_REQ_OU         "' + str(ou) + '"\n' + \
           'set_var EASYRSA_ALGO           "ec"\nset_var EASYRSA_DIGEST         "sha512"'

    file = open("vars", "w+")
    file.write(stri)
    file.close()

    shutil.move("vars", "../easy-rsa")

    command_path = "export PATH=$PATH:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games:/snap/bin; "
    command_work = "cd ~/easy-rsa; echo yes | ./easyrsa build-ca nopass"
    command = command_path + command_work
    result = subprocess.run(command, \
                            stderr=subprocess.PIPE, \
                            stdout=subprocess.PIPE, \
                            shell=True, \
                            encoding='utf-8')

    command_work = "cd ~/easy-rsa; rm vars"
    command = command_path + command_work
    result = subprocess.run(command, \
                            stderr=subprocess.PIPE, \
                            stdout=subprocess.PIPE, \
                            shell=True, \
                            encoding='utf-8')

    return render_template('server/index.html')


@server.route('/')
def index():
    return render_template('server/index.html')
