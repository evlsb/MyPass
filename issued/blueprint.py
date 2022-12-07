from flask import Blueprint, render_template, redirect, url_for
from models import Clients
from app import db
from flask_security import login_required

issued = Blueprint('issued', __name__, template_folder='templates')


@issued.route('/save/<int:id>')
def save(id):
    client = Clients.query.filter(Clients.id==id).first()
    return render_template('issued/code.html', client=client)


@issued.route('/')
def index():
    clients = Clients.query.all()
    # clients = Clients.query.filter(Clients.id == 2).first()
    return render_template('issued/index.html', clients=clients)


@issued.route('/delete/<int:id>')
def delete(id):
    client = Clients.query.filter(Clients.id==id).delete()
    db.session.commit()

    return redirect(url_for('issued.index'))