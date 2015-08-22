from nosferatu import db
from sqlalchemy.dialects import postgresql 


class Node(db.Model):
    __tablename__ = 'nodes'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    ip_addr = db.Column(postgresql.INET)
    mac_addr = db.Column(postgresql.MACADDR)

    def __init__(self, name, ip_addr, mac_addr):
        self.url = url
        self.ip_addr = ip_addr
        self.mac_addr = mac_addr

    def __repr__(self):
        return '<id {}>'.format(self.id)

