# Zawiera endpointy dla aplikacji
# To tutaj definiowane jest, co ma się stać, gdy użytkownik odwiedzi określony adres URL
from app import app, db
from flask import render_template
from app.models import User


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/testdb')
def testdb():
    try:
        user = User(first_name="Kasia", last_name="Januszek", user_type="administrator", password="test1234")
        db.session.add(user)
        db.session.commit()
        return "Dodano rekord!"
    except:
        return "Nie udało się dodać rekordu!"
