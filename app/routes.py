# Zawiera endpointy dla aplikacji
# To tutaj definiowane jest, co ma się stać, gdy użytkownik odwiedzi określony adres URL
from app import app, db
from flask import request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import User


@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    hashed_password = generate_password_hash(data['password'], method='pbkdf2:sha256')
    new_user = User(
        first_name=data['first_name'],
        last_name="admin",
        user_type="administrator",
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
