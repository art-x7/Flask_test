from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


class Tpp(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    process = db.Column(db.Text, nullable=False)
    tpp_stage = db.Column(db.Text, nullable=False)
    prod_name = db.Column(db.Text, nullable=False)
    lot_name = db.Column(db.Text, nullable=False)
    qty_in = db.Column(db.Integer, nullable=False)
    qty_out = db.Column(db.Integer, nullable=False)
    defects = db.Column(db.Text, nullable=False)
    materials = db.Column(db.Text, nullable=False)
    tool_name = db.Column(db.Text, nullable=False)
    recipe = db.Column(db.Text, nullable=False)
    time_s = db.Column(db.Text, nullable=False)
    time_p = db.Column(db.Text, nullable=False)
    uph = db.Column(db.Integer, nullable=False)
    wafer_name = db.Column(db.Text, nullable=False)
    warpage = db.Column(db.Text, nullable=False)
    info = db.Column(db.Text, nullable=False)
    comment = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    date_input = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    def __repr__(self):
        return f'<Tpp {self.id}>'


class Tpp_config(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    prod_name = db.Column(db.Text, nullable=False)
    tpp_stage = db.Column(db.Text, nullable=False)
    number = db.Column(db.Text, nullable=False)
    owner = db.Column(db.Text, nullable=False)
    comment = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f'<Tpp_config {self.id}>'


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(64), index=True, unique=True)
    password_hash = db.Column(db.String(120), index=True, unique=True)
    time = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    tpp = db.relationship('Tpp', backref='author', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.id} by {self.login}>'
