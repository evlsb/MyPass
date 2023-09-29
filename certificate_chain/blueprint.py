from flask import Blueprint, render_template, redirect, url_for, request
from models import CA
from app import db
import uuid
import random
import datetime
from OpenSSL import crypto

certificate_chain = Blueprint('certificate_chain', __name__, template_folder='templates')


@certificate_chain.route('/')
def index():
    ca = CA.query.all()
    servers = []
    cas = []
    for i in range(len(ca)):
        cas.append(ca[i].name)
        servers.append(ca[i].server)
        # print(ca[i].server)

    #server = ca.server
    print(cas)
    print(servers)

    return render_template('certificate_chain/index.html', ca=ca)