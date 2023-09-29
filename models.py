from app import db
from datetime import datetime

from flask_security import UserMixin, RoleMixin



ca_server = db.Table('ca_server',
                       db.Column('ca_id', db.Integer(), db.ForeignKey('ca.id', ondelete="CASCADE")),
                       db.Column('server_id', db.Integer(), db.ForeignKey('server.id', ondelete="CASCADE"))
                       )

server_client = db.Table('server_client',
                       db.Column('server_id', db.Integer(), db.ForeignKey('server.id', ondelete="CASCADE")),
                       db.Column('client_id', db.Integer(), db.ForeignKey('client.id', ondelete="CASCADE"))
                       )

class CA(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String(150))
    title = db.Column(db.String(150))
    name = db.Column(db.String(150))
    description = db.Column(db.String(300))
    cert_ca = db.Column(db.Text, nullable=False)
    key_ca = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    server = db.relationship('Server', secondary=ca_server, backref=db.backref('ca', lazy='dynamic'))


class Server(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String(150))
    title = db.Column(db.String(150))
    name = db.Column(db.String(150))
    description = db.Column(db.String(300))
    cert_server = db.Column(db.Text, nullable=False)
    key_server = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    client = db.relationship('Client', secondary=server_client, backref=db.backref('server', lazy='dynamic'))

    def __repr__(self):
        return self.name


class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String(150))
    title = db.Column(db.String(150))
    name = db.Column(db.String(150))
    description = db.Column(db.String(300))
    cert_client = db.Column(db.Text, nullable=False)
    key_client = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return self.name







roles_users = db.Table('roles_users',
                       db.Column('user_id', db.Integer(), db.ForeignKey('user.id', ondelete="CASCADE")),
                       db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))
                       )


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime)
    roles = db.relationship('Role', secondary=roles_users, backref=db.backref('users', lazy='dynamic'))


class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    description = db.Column(db.String(255))



# ---------------------------------------------------------


