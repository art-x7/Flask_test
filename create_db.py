from main import db


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

    def __repr__(self):
        return '<Tpp %r>' % self.id


class Tpp_config(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    prod_name = db.Column(db.Text, nullable=False)
    tpp_stage = db.Column(db.Text, nullable=False)
    comment = db.Column(db.Text, nullable=False)
    
    def __repr__(self):
        return '<Tpp_config %r>' % self.id
        