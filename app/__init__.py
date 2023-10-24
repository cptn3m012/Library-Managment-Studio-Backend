# Inicjalizacja aplikacji Flask oraz innych modułów
# Tutaj tworzona jest instancja aplikacji wraz z konfiguracją
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS


app = Flask(__name__)
CORS(app)
app.config.from_object('config.Config')
db = SQLAlchemy(app)

migrate = Migrate(app, db)
from app import routes, models
