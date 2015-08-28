from flask_user import UserMixin
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects import postgresql

from nosferatu import db


class Node(db.Model):
    __tablename__ = 'nodes'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(35), nullable=False)
    ip_addr = db.Column(postgresql.INET)
    mac_addr = db.Column(postgresql.MACADDR)
    user_id = db.Column(db.Integer, ForeignKey('users.id'))

    def __init__(self, name, ip_addr, mac_addr):
        self.name = name
        self.ip_addr = ip_addr
        self.mac_addr = mac_addr

    def __repr__(self):
        return '<id {}>'.format(self.id)


class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)

    # User authentication information (required for Flask-User)
    email = db.Column(db.Unicode(255), nullable=False, server_default='', unique=True)
    confirmed_at = db.Column(db.DateTime())
    password = db.Column(db.String(255), nullable=False, server_default='')
    reset_password_token = db.Column(db.String(100), nullable=False, server_default='')
    active = db.Column(db.Boolean(), nullable=False, server_default='0')

    nodes = relationship('Node', backref='owner')

    def __repr__(self):
        return '<id {}, {}>'.format(self.id, self.username)
