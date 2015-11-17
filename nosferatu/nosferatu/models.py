from flask_user import UserMixin
from sqlalchemy import ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects import postgresql

from nosferatu import db


class Node(db.Model):
    __tablename__ = 'nodes'

    id = db.Column(db.Integer, primary_key=True)
    mac_addr = db.Column(postgresql.MACADDR)

    name = db.Column(db.String(35), nullable=False)
    ip_addr = db.Column(postgresql.INET)

    relay_status = db.Column(db.Boolean, default=False)

    user_id = db.Column(db.Integer, ForeignKey('users.id'))
    rules = relationship('Rule', backref='nodes', foreign_keys='[Rule.node]')

    def __init__(self, name, ip_addr, mac_addr, user_id):
        self.name = name
        self.ip_addr = ip_addr
        self.mac_addr = mac_addr
        user_id = user_id

    def __repr__(self):
        return '<id {}>'.format(self.id)

    def to_json(self):
        return {
            'id': self.id,
            'mac': self.mac_addr,
            'name': self.name,
            'ip_addr': self.ip_addr,
            'relay_status': self.relay_status,
        }


# schedule_types = ['Auto', 'Manual']
# time_of_day = ['Sunset', 'Sunrise']
# ScheduleTypes(*schedule_types, name='ScheduleTypes')
# TimeOfDay(*time_of_day, name='TimeOfDay')

class Rule(db.Model):
    __tablename__ = 'rules'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), primary_key=True, nullable=False)

    type = db.Column(db.String(255), nullable=False)
    turn_on = db.Column(db.Boolean(), nullable=False)
    days = db.Column(db.String(56), nullable=False)

    # Schedules
    schedule_type = db.Column(db.String(56), nullable=False)

    # - Manual
    sched_hour = db.Column(db.Integer)
    sched_minute = db.Column(db.Integer)

    # - Auto
    sched_zip_code = db.Column(db.Integer)
    sched_time_of_day = db.Column(db.String(56))

    # Events
    event_node = db.Column(db.Integer, ForeignKey('nodes.id'), nullable=True)
    event_node_state = db.Column(db.Boolean, default=False)

    # Parent Node
    node = db.Column(db.Integer, ForeignKey('nodes.id'))

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __repr__(self):
        return '<id {}, {}>'.format(self.id, self.username)


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
