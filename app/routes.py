# Zawiera endpointy dla aplikacji
# To tutaj definiowane jest, co ma się stać, gdy użytkownik odwiedzi określony adres URL
from app import app, db
from flask import render_template, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import User


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    hashed_password = generate_password_hash(data['password'], method='sha256')
    new_user = User(
        first_name=data['first_name'],
        last_name=data['last_name'],
        user_type=data['user_type'],
        password=hashed_password
    )
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'Registered successfully'}), 201


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(first_name=data['first_name']).first()
    if user and check_password_hash(user.password, data['password']):
              return jsonify({'message': 'Login successful'}), 200
    return jsonify({'message': 'Invalid credentials'}), 401


@app.route('/testdb')
def testdb():
    try:
        user = User(first_name="Kasia", last_name="Januszek", user_type="administrator", password="test1234")
        db.session.add(user)
        db.session.commit()
        return "Dodano rekord!"
    except:
        return "Nie udało się dodać rekordu!"
