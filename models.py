from main import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


class Tpp(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    process_id = db.Column(db.Integer, db.ForeignKey('process.id'))
    prod_id = db.Column(db.Integer, db.ForeignKey('tpp_config.id'))
    lot_name = db.Column(db.Text, nullable=False)
    qty_in = db.Column(db.Integer, nullable=False)
    qty_out = db.Column(db.Integer, nullable=False)
    defects = db.Column(db.Text, nullable=False)
    materials_id = db.Column(db.Integer, db.ForeignKey('materials.id'))
    volume_materials = db.Column(db.Float, nullable=False)
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.id'))
    tool_id = db.Column(db.Integer, db.ForeignKey('tool.id'))
    recipe = db.Column(db.Text, nullable=False)
    time_s = db.Column(db.Text, nullable=False)
    time_p = db.Column(db.Text, nullable=False)
    uph = db.Column(db.Integer, nullable=False)
    wafer_name = db.Column(db.Text, nullable=False)
    warpage = db.Column(db.Text, nullable=False)
    willingness = db.Column(db.Text, nullable=False)
    comment = db.Column(db.Text, nullable=False)
    risk = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    date_input = db.Column(db.DateTime, index=True, default=datetime.utcnow)        

    def __repr__(self):
        return f'<Tpp {self.id}>'


class Tpp_config(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    prod_sum = db.Column(db.Text, nullable=False)
    owner = db.Column(db.Text, nullable=False)
    comment = db.Column(db.Text, nullable=False)
    status = db.Column(db.Text, nullable=False, default="Открыт")
    del_status = db.Column(db.Boolean, nullable=False, default=True)

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


class Materials(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    process_id = db.Column(db.Integer, db.ForeignKey('process.id'))
    material = db.Column(db.Text, nullable=False)
    unit = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f'<Materials {self.id} of {self.material}>'


class Equipment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    process_id = db.Column(db.Integer, db.ForeignKey('process.id'))
    main = db.Column(db.Text, nullable=False)
 
    
    def __repr__(self):
        return f'<Equipment {self.id} of {self.main}>'


class Tool(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tool = db.Column(db.Text, nullable=False)
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.id'))

    def __repr__(self):
        return f'<Tool {self.id} of {self.tool}>'


class Process(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    process = db.Column(db.Text, nullable=False)
    branch = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f'<Process {self.id} of {self.process}>'


class Uph(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tpp_id = db.Column(db.Integer, db.ForeignKey('tpp_config.id'))
    process_id = db.Column(db.Integer, db.ForeignKey('process.id'))
    plan_uph = db.Column(db.Integer, nullable=False) 
    
    def __repr__(self):
        return f'<Uph {self.id}>'
