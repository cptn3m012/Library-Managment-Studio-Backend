# Inicjalizacja aplikacji Flask oraz innych modułów
# Tutaj tworzona jest instancja aplikacji wraz z konfiguracją
from flask import Flask

app = Flask(__name__)

from app import routes, models
