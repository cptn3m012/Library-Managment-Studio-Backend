# Zawiera endpointy dla aplikacji
# To tutaj definiowane jest, co ma się stać, gdy użytkownik odwiedzi określony adres URL
from app import app
from flask import render_template


@app.route('/')
def index():
    return render_template('index.html')