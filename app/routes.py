# Zawiera endpointy dla aplikacji.
# To tutaj definiowane jest, co ma się stać, gdy użytkownik odwiedzi określony adres URL.
from app import app, db
from flask import request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app.models import User, Employee, Category, Book, Author, book_author
from datetime import datetime


# Endpoint do logowania użytkownika. Sprawdza, czy dane logowania są poprawne i zwraca token JWT.
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


# Endpoint do pobierania danych o konkretnym użytkowniku na podstawie jego ID.
@app.route('/users/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify({'username': user.username}), 200


# Endpoint do aktualizacji danych konkretnego użytkownika. Umożliwia zmianę nazwy użytkownika i hasła.
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


# Endpoint do dodawania nowego pracownika. Tworzy zarówno rekord pracownika, jak i powiązany rekord użytkownika.
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


# Endpoint do pobierania listy wszystkich pracowników.
@app.route('/api/employees', methods=['GET'])
def get_employees():
    employees = Employee.query.all()
    employees_data = [{
        'id': emp.id,
        'first_name': emp.first_name,
        'last_name': emp.last_name,
        'email': emp.email,
        'phone_number': emp.phone_number,
        'pesel': emp.pesel,
        'hired_date': emp.hired_date.strftime("%Y-%m-%d") if emp.hired_date else None
    } for emp in employees]

    return jsonify(employees_data)


# Endpoint do aktualizacji danych konkretnego pracownika na podstawie jego ID.
@app.route('/api/employees/<int:employee_id>', methods=['PUT'])
def update_employee(employee_id):
    employee = Employee.query.get_or_404(employee_id)
    user = User.query.get_or_404(employee.user_id)
    data = request.json

    # Aktualizacja danych pracownika
    employee.first_name = data.get('first_name', employee.first_name)
    employee.last_name = data.get('last_name', employee.last_name)
    employee.pesel = data.get('pesel', employee.pesel)
    employee.phone_number = data.get('phone_number', employee.phone_number)
    employee.email = data.get('email', employee.email)

    # Aktualizacja e-maila w tabeli User
    if 'email' in data:
        user.username = data['email']

    # Opcjonalnie, aktualizacja daty zatrudnienia, jeśli jest dostarczona
    if 'hired_date' in data:
        employee.hired_date = datetime.strptime(data['hired_date'], '%Y-%m-%d')

    db.session.commit()
    return jsonify({'message': 'Dane pracownika zaktualizowane'}), 200


# Endpoint do usuwania konkretnego pracownika (i powiązanego użytkownika) na podstawie jego ID.
@app.route('/api/employees/<int:employee_id>', methods=['DELETE'])
def delete_employee(employee_id):
    employee = Employee.query.get_or_404(employee_id)

    # Usuwanie powiązanego użytkownika
    if employee.user_id:
        user = User.query.get(employee.user_id)
        if user:
            db.session.delete(user)

    db.session.delete(employee)
    db.session.commit()
    return jsonify({'message': 'Pracownik usunięty z bazy danych'}), 200


# Endpoint do pobierania danych o aktualnie zalogowanym użytkowniku.
@app.route('/api/get-current-user', methods=['GET'])
@jwt_required()
def get_current_user():
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user['username']).first()

    if user:
        return jsonify({'username': user.username}), 200
    else:
        return jsonify({'message': 'Użytkownik nie znaleziony'}), 404


# Endpoint do zmiany hasła przez użytkownika.
@app.route('/api/change-password', methods=['POST'])
@jwt_required()
def change_password():
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user['username']).first()

    if not user:
        return jsonify({'message': 'Użytkownik nie znaleziony'}), 404

    data = request.get_json()
    old_password = data.get('oldPassword')
    new_password = data.get('newPassword')

    if not user.check_password(old_password):
        return jsonify({'message': 'Stare hasło jest nieprawidłowe'}), 401

    if not new_password:
        return jsonify({'message': 'Nowe hasło nie może być puste'}), 400

    user.set_password(new_password)
    db.session.commit()

    return jsonify({'message': 'Hasło zostało zmienione'}), 200


# Endpoint do aktualizacji nazwy użytkownika przez użytkownika.
@app.route('/api/update-username', methods=['PUT'])
@jwt_required()
def update_username():
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user['username']).first()

    if not user:
        return jsonify({'message': 'Użytkownik nie znaleziony'}), 404

    data = request.get_json()
    new_username = data.get('newUsername')

    if not new_username:
        return jsonify({'message': 'Nowa nazwa użytkownika nie może być pusta'}), 400

    # Sprawdzenie, czy nowa nazwa użytkownika już istnieje
    if User.query.filter_by(username=new_username).first():
        return jsonify({'message': 'Nazwa użytkownika jest już zajęta'}), 400

    user.username = new_username
    db.session.commit()

    return jsonify({'message': 'Nazwa użytkownika została zaktualizowana'}), 200


# Endpoint do dodawania nowej kategorii.
@app.route('/api/categories', methods=['POST'])
def add_category():
    data = request.json
    name = data.get('name')

    if not name:
        return jsonify({'error': 'Nazwa kategorii jest wymagana'}), 400

    new_category = Category(name=name)
    db.session.add(new_category)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

    return jsonify({'message': 'Kategoria została pomyślnie dodana', 'category_id': new_category.id}), 201


# Endpoint do pobierania listy wszystkich kategorii.
@app.route('/api/categories', methods=['GET'])
def get_categories():
    categories = Category.query.all()
    categories_data = [{'id': cat.id, 'name': cat.name} for cat in categories]

    return jsonify(categories_data)


#Endpoint do dodawania nowej książki do bazy.
@app.route('/api/books', methods=['POST'])
def add_book():
    data = request.json
    title = data.get('title')
    isbn = data.get('isbn')
    category_id = data.get('category')
    description = data.get('description')
    quantity = data.get('quantity', 1)
    authors = data.get('authors')

    if not title or not isbn or not category_id or not quantity:
        return jsonify({'error': 'Brakujące dane książki'}), 400

    # Sprawdzenie, czy książka o tym samym ISBN już istnieje
    existing_book = Book.query.filter_by(isbn=isbn).first()
    if existing_book:
        return jsonify({'error': 'Książka z tym ISBN już istnieje'}), 400

    new_book = Book(
        title=title,
        isbn=isbn,
        category_id=category_id,
        description=description,
        quantity=quantity,
    )

    db.session.add(new_book)

    for author in authors:
        first_name = author.get('firstName')
        last_name = author.get('lastName')
        existing_author = Author.query.filter_by(first_name=first_name, last_name=last_name).first()
        if not existing_author:
            existing_author = Author(first_name=first_name, last_name=last_name)
            db.session.add(existing_author)
            db.session.flush()
        association = book_author.insert().values(book_id=new_book.id, author_id=existing_author.id)
        db.session.execute(association)

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

    return jsonify({'message': 'Książka dodana pomyślnie', 'book_id': new_book.id}), 201




