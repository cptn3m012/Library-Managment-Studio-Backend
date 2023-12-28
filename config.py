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
    SECURITY_PASSWORD_SALT = os.getenv('SECURITY_PASSWORD_SALT')

    # Konfiguracja SMTP dla Gmaila
    MAIL_SERVER = os.getenv('MAIL_SERVER')
    MAIL_PORT = int(os.getenv('MAIL_PORT'))
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS') == 'False'
    MAIL_USE_SSL = os.getenv('MAIL_USE_SSL') == 'True'