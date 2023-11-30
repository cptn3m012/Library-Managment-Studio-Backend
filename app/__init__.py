# Inicjalizacja aplikacji Flask oraz innych modułów
# Tutaj tworzona jest instancja aplikacji wraz z konfiguracją
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_jwt_extended import JWTManager


app = Flask(__name__)
CORS(app)
app.config.from_object('config.Config')
db = SQLAlchemy(app)
jwt = JWTManager(app)

migrate = Migrate(app, db)
from app import routes, models
