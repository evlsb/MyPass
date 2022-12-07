from app import db
from datetime import datetime

from flask_security import UserMixin, RoleMixin


class Clients(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150))
    name = db.Column(db.String(150))
    description = db.Column(db.String(300))
    crt = db.Column(db.Text, nullable=False)
    key = db.Column(db.Text, nullable=False)
    ta = db.Column(db.Text, nullable=False)
    cert_ca = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, title, name, description, crt, key, ta, cert_ca):
        self.title = title
        self.name = name
        self.description = description
        self.crt = crt
        self.key = key
        self.ta = ta
        self.cert_ca = cert_ca

    def __repr__(self):
        return '<Client %r>' % self.id


### Flask Security

roles_users = db.Table('roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))
)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    roles = db.relationship('Role', secondary=roles_users, backref=db.backref('users', lazy='dynamic'))


class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    description = db.Column(db.String(255))