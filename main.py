from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

from config import Config
from routes import app_routes


app = Flask(__name__)
app.register_blueprint(app_routes)
app.config.from_object(Config)
db = SQLAlchemy(app)
login = LoginManager(app)
login.login_view = 'auth.login'

with app.app_context():
    from models import *
    
    db.create_all()


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=True)
