# Plik konfiguracyjny dla aplikacji
# Zawiera różne ustawienia
import os
from dotenv import load_dotenv
from datetime import timedelta

# Wczytuje dane z pliku .env
load_dotenv()

class Config:
    # Konfiguracja bazy danych
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv('SECRET_KEY')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=8)