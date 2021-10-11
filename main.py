from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from routes import app_routes

app = Flask(__name__)
app.register_blueprint(app_routes)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///tpp.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

with app.app_context():
    from models import *
    
    db.create_all()


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=True)
