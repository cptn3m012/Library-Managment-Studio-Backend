# Zawiera endpointy dla aplikacji
# To tutaj definiowane jest, co ma się stać, gdy użytkownik odwiedzi określony adres URL
from app import app, db
from flask import request, jsonify
from flask_jwt_extended import create_access_token, jwt_required
from app.models import User, Employee
from datetime import datetime


@app.route('/users/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        access_token = create_access_token(identity={'username': username, 'role_id': user.role_id})
        return jsonify(access_token=access_token), 200

    return jsonify({'message': 'Nieprawidłowy login lub hasło'}), 401


@app.route('/users/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify({'username': user.username}), 200


@app.route('/users/<int:user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    user = User.query.get_or_404(user_id)
    data = request.get_json()

    user.username = data.get('username', user.username)
    if 'password' in data:
        user.set_password(data['password'])

    db.session.commit()
    return jsonify({'message': 'Dane użytkownika zaktualizowane'}), 200


@app.route('/add-employee', methods=['POST'])
def add_employee():
    data = request.json

    # Walidacja danych
    required_fields = ['first_name', 'last_name', 'pesel', 'email', 'password']
    if any(field not in data for field in required_fields):
        return jsonify({'error': 'Brak wymaganych danych'}), 400

    # Sprawdzanie, czy użytkownik z tym adresem e-mail już istnieje
    if User.query.filter_by(username=data['email']).first():
        return jsonify({'error': 'Użytkownik z tym adresem e-mail już istnieje'}), 400

    # Tworzenie użytkownika
    new_user = User(
        username=data['email'],
        role_id=2  # Stałe role_id dla pracownika
    )
    new_user.set_password(data['password'])

    # Tworzenie pracownika
    new_employee = Employee(
        first_name=data['first_name'],
        last_name=data['last_name'],
        email=data['email'],
        phone_number=data.get('phone_number'),
        pesel=data['pesel'],
        hired_date=datetime.strptime(data.get('hired_date'), '%Y-%m-%d') if data.get('hired_date') else None,
        user=new_user  # Powiązanie pracownika z użytkownikiem
    )

    db.session.add(new_employee)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

    return jsonify({'message': 'Pracownik dodany pomyślnie', 'employee_id': new_employee.id}), 201
