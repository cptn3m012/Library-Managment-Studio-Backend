# Zawiera endpointy dla aplikacji.
# To tutaj definiowane jest, co ma się stać, gdy użytkownik odwiedzi określony adres URL.
import smtplib

from sqlalchemy import func

from app import app, db
from flask import request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app.models import User, Employee, Category, Book, Author, book_author, Borrower, Loan, Role, LoanHistory
from datetime import datetime
from itsdangerous import URLSafeTimedSerializer
from email.mime.text import MIMEText
from sqlalchemy.exc import IntegrityError


# Endpoint do logowania użytkownika. Sprawdza, czy dane logowania są poprawne i zwraca token JWT.
@app.route('/users/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    # Sprawdzenie, czy użytkownik istnieje
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({'message': 'Nie znaleziono użytkownika z podanym adresem e-mail'}), 404

    # Weryfikacja hasła
    if not user.check_password(password):
        return jsonify({'message': 'Nieprawidłowe hasło'}), 401

    # Generowanie tokena JWT
    access_token = create_access_token(identity={'username': username, 'role_id': user.role_id})
    return jsonify(access_token=access_token), 200


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

    # Sprawdzenie unikatowości PESEL
    if Employee.query.filter(Employee.pesel == data['pesel'], Employee.id != employee_id).first():
        return jsonify({'error': 'Pracownik o podanym PESEL jest już w systemie'}), 400

    # Sprawdzenie unikatowości numeru telefonu
    if Employee.query.filter(Employee.phone_number == data['phone_number'], Employee.id != employee_id).first():
        return jsonify({'error': 'Pracownik o podanym numerze telefonu jest już w systemie'}), 400

    # Sprawdzenie unikatowości emaila
    if User.query.filter(User.username == data['email'], User.id != user.id).first():
        return jsonify({'error': 'Pracownik o podanym emailu jest już w systemie'}), 400

    try:
        # Aktualizacja danych pracownika
        employee.first_name = data.get('first_name', employee.first_name)
        employee.last_name = data.get('last_name', employee.last_name)
        employee.pesel = data.get('pesel', employee.pesel)
        employee.phone_number = data.get('phone_number', employee.phone_number)
        user.username = data.get('email', user.username)

        # Opcjonalnie, aktualizacja daty zatrudnienia
        if 'hired_date' in data:
            employee.hired_date = datetime.strptime(data['hired_date'], '%Y-%m-%d')

        db.session.commit()
        return jsonify({'message': 'Dane pracownika zaktualizowane'}), 200
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'Błąd podczas aktualizacji danych pracownika'}), 400


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


# Endpoint do zmiany hasła przez użytkownika.
@app.route('/api/change-password', methods=['POST'])
@jwt_required()
def change_password():
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user['username']).first()

    print(current_user['username'])
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


# Funkcja do generowania tokena JWT
def generate_jwt_token(user):
    return create_access_token(identity={'username': user.username, 'role_id': user.role_id})


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

    new_token = generate_jwt_token(user)

    return jsonify({'newToken': new_token}), 200


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


# Endpoint do dodawania nowej książki do bazy.
@app.route('/api/books', methods=['POST'])
def add_book():
    data = request.json
    title = data.get('title')
    isbn = data.get('isbn')
    category_id = data.get('category')
    publication_year = data.get('publication_year')
    publisher = data.get('publisher')
    quantity = data.get('quantity', 1)
    authors = data.get('authors')

    if not title or not isbn or not category_id or not publication_year or not publisher or not quantity:
        return jsonify({'error': 'Brakujące dane książki'}), 400

    # Sprawdzenie, czy książka o tym samym ISBN już istnieje
    existing_book = Book.query.filter_by(isbn=isbn).first()
    if existing_book:
        return jsonify({'error': 'Książka z tym ISBN już istnieje'}), 400

    new_book = Book(
        title=title,
        isbn=isbn,
        category_id=category_id,
        publication_year=publication_year,
        publisher=publisher,
        quantity=quantity
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


@app.route('/api/books', methods=['GET'])
def get_books():
    # Pobieranie wszystkich książek wraz z kategoriami i autorami
    books = Book.query.all()
    books_data = []
    for book in books:
        # Przetwarzanie autorów książki
        authors_data = [{'firstName': author.first_name, 'lastName': author.last_name} for author in book.authors]
        # Dodawanie danych książki do listy
        books_data.append({
            'id': book.id,
            'title': book.title,
            'isbn': book.isbn,
            'category': book.category.name if book.category else 'Brak kategorii',
            'publication_year': book.publication_year,
            'publisher': book.publisher,
            'quantity': book.quantity,
            'status': book.status,
            'authors': authors_data
        })
    return jsonify(books_data), 200


@app.route('/api/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    book = Book.query.get_or_404(book_id)

    if book.quantity > 1:
        book.quantity -= 1
    else:
        # Usunięcie powiązań książki z autorami
        for author in book.authors:
            book.authors.remove(author)
        db.session.delete(book)

    try:
        db.session.commit()
        return jsonify({'message': 'Książka została usunięta'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@app.route('/api/books/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    book = Book.query.get_or_404(book_id)
    data = request.json

    title = data.get('title')
    isbn = data.get('isbn')
    category_id = data.get('category')
    publication_year = data.get('publication_year')
    publisher = data.get('publisher')
    authors = data.get('authors')

    if not title or not isbn or not category_id or not publication_year or not publisher:
        return jsonify({'error': 'Brakujące dane książki'}), 400

    # Sprawdzenie unikalności numeru ISBN (pomijając aktualnie edytowaną książkę)
    existing_book_with_isbn = Book.query.filter(Book.isbn == isbn, Book.id != book_id).first()
    if existing_book_with_isbn:
        return jsonify({'error': 'Książka z tym numerem ISBN już istnieje'}), 400

    book.title = title
    book.isbn = isbn
    book.category_id = category_id
    book.publication_year = publication_year
    book.publisher = publisher

    # Usunięcie obecnych autorów książki
    for author in book.authors:
        book.authors.remove(author)

    # Dodanie nowych autorów książki
    for author_data in authors:
        first_name = author_data.get('firstName')
        last_name = author_data.get('lastName')

        if not first_name or not last_name:
            return jsonify({'error': 'Imię i nazwisko autora są wymagane'}), 400

        author = Author.query.filter_by(first_name=first_name, last_name=last_name).first()
        if not author:
            author = Author(first_name=first_name, last_name=last_name)
            db.session.add(author)
            db.session.flush()

        association = book_author.insert().values(book_id=book.id, author_id=author.id)
        db.session.execute(association)

    try:
        db.session.commit()
        return jsonify({'message': 'Książka zaktualizowana pomyślnie', 'book_id': book.id}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# Endpoint do usuwania kategorii na podstawie jej ID.
@app.route('/api/categories/<int:category_id>', methods=['DELETE'])
def delete_category(category_id):
    category = Category.query.get_or_404(category_id)

    # Sprawdzenie, czy kategoria jest powiązana z jakimiś książkami
    if category.books:
        # Dodatkowe sprawdzenie, czy kategoria jest powiązana tylko z książką, która jest aktualnie edytowana
        current_book_id = request.args.get('current_book_id')
        if current_book_id and len(category.books) == 1 and category.books[0].id == int(current_book_id):
            # Można usunąć kategorię, jeśli jest powiązana tylko z aktualnie edytowaną książką
            pass
        else:
            return jsonify({'error': 'Kategoria jest powiązana z książkami i nie może zostać usunięta'}), 400

    db.session.delete(category)
    try:
        db.session.commit()
        return jsonify({'message': 'Kategoria usunięta pomyślnie'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# Endpoint do dodawania książki
@app.route('/add-reader', methods=['POST'])
def add_reader():
    data = request.json
    print("Otrzymane dane:", data)

    # Walidacja danych
    required_fields = ['first_name', 'last_name', 'email', 'phone_number', 'pesel', 'address', 'postalCodeAndCity']
    if any(field not in data for field in required_fields):
        return jsonify({'error': 'Brak wymaganych danych'}), 400

    # Sprawdzanie, czy czytelnik z tym adresem e-mail lub numerem telefonu już istnieje
    if Borrower.query.filter_by(pesel=data['pesel']).first():
        return jsonify({'error': 'Czytelnik z tym peslem już istnieje'}), 400

    if Borrower.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Czytelnik z tym adresem e-mail już istnieje'}), 400

    if Borrower.query.filter_by(phone_number=data['phone_number']).first():
        return jsonify({'error': 'Czytelnik z tym numerem telefonu już istnieje'}), 400

    postal_code_and_city = data['postalCodeAndCity'].split(maxsplit=1)
    if len(postal_code_and_city) != 2:
        return jsonify({'error': 'Nieprawidłowy format kodu pocztowego i miejscowości'}), 400

    postal_code, city = postal_code_and_city

    # Tworzenie nowego czytelnika
    new_reader = Borrower(
        first_name=data['first_name'],
        last_name=data['last_name'],
        email=data['email'],
        phone_number=data['phone_number'],
        pesel=data['pesel'],
        address=data['address'],
        postal_code=postal_code,
        city=city
    )

    db.session.add(new_reader)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

    return jsonify({'message': 'Czytelnik dodany pomyślnie', 'reader_id': new_reader.id}), 201


@app.route('/api/readers', methods=['GET'])
def get_all_readers():
    # Pobranie wszystkich czytelników z bazy danych
    all_readers = Borrower.query.all()

    # Przygotowanie listy danych wszystkich czytelników do odpowiedzi
    readers_data = [{
        'id': reader.id,
        'first_name': reader.first_name,
        'last_name': reader.last_name,
        'email': reader.email,
        'phone_number': reader.phone_number,
        'pesel': reader.pesel,
        'address': reader.address,
        'postal_code': reader.postal_code,
        'city': reader.city
    } for reader in all_readers]

    return jsonify(readers_data), 200


@app.route('/api/readers/<int:reader_id>', methods=['DELETE'])
def delete_reader(reader_id):
    reader = Borrower.query.get_or_404(reader_id)

    # Sprawdzenie, czy czytelnik ma aktywne wypożyczenia
    active_loans = Loan.query.filter_by(borrower_id=reader_id, status='Wypożyczona').all()
    if active_loans:
        # Zwrócenie błędu, jeśli istnieją aktywne wypożyczenia
        return jsonify({'error': 'Nie można usunąć czytelnika, który ma wypożyczone książki'}), 400

    # Brak aktywnych wypożyczeń - można bezpiecznie usunąć czytelnika
    db.session.delete(reader)
    try:
        db.session.commit()
        return jsonify({'message': 'Czytelnik został usunięty'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@app.route('/api/readers/<int:reader_id>', methods=['PUT'])
def update_reader(reader_id):
    reader = Borrower.query.get_or_404(reader_id)
    data = request.get_json()

    # Walidacja danych
    required_fields = ['first_name', 'last_name', 'email', 'phone_number', 'pesel', 'address', 'postalCodeAndCity']
    if any(field not in data for field in required_fields):
        return jsonify({'error': 'Brak wymaganych danych'}), 400

    # Sprawdzanie, czy podane dane już istnieją dla innego czytelnika
    if data['email'] != reader.email and Borrower.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Czytelnik z tym adresem e-mail już istnieje'}), 400

    if data['phone_number'] != reader.phone_number and Borrower.query.filter_by(
            phone_number=data['phone_number']).first():
        return jsonify({'error': 'Czytelnik z tym numerem telefonu już istnieje'}), 400

    if data['pesel'] != reader.pesel and Borrower.query.filter_by(pesel=data['pesel']).first():
        return jsonify({'error': 'Czytelnik z tym peselem już istnieje'}), 400

    # Rozdzielenie `postalCodeAndCity` na `postal_code` i `city`
    postal_code_and_city = data['postalCodeAndCity'].split(maxsplit=1)
    if len(postal_code_and_city) != 2:
        return jsonify({'error': 'Nieprawidłowy format kodu pocztowego i miejscowości'}), 400
    postal_code, city = postal_code_and_city

    # Updating reader details
    reader.first_name = data.get('first_name', reader.first_name)
    reader.last_name = data.get('last_name', reader.last_name)
    reader.email = data['email']
    reader.phone_number = data['phone_number']
    reader.pesel = data.get('pesel', reader.pesel)
    reader.address = data.get('address', reader.address)
    reader.postal_code = postal_code
    reader.city = city

    try:
        db.session.commit()
        return jsonify({'message': 'Dane czytelnika zaktualizowane'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@app.route('/api/borrowers', methods=['GET'])
def get_borrowers():
    borrowers = Borrower.query.all()
    borrowers_data = [{
        'id': borrower.id,
        'first_name': borrower.first_name,
        'last_name': borrower.last_name,
        'pesel': borrower.pesel
    } for borrower in borrowers]

    return jsonify(borrowers_data), 200


@app.route('/api/loans', methods=['POST'])
def create_loan():
    data = request.get_json()

    # Walidacja danych
    required_fields = ['book_ids', 'borrower_id', 'loan_date', 'return_date']
    if any(field not in data for field in required_fields):
        return jsonify({'error': 'Brak wymaganych danych'}), 400

    book_ids = data['book_ids']
    borrower_id = data['borrower_id']
    loan_date = data['loan_date']
    return_date = data['return_date']

    if not isinstance(book_ids, list) or not book_ids:
        return jsonify({'error': 'Nieprawidłowy format book_ids'}), 400

    loans = []
    for book_id in book_ids:
        # Pobranie książki
        book = Book.query.get(book_id)
        if not book:
            return jsonify({'error': f'Nie znaleziono książki o ID: {book_id}'}), 404

        # Sprawdzenie, czy książka jest dostępna
        if book.quantity <= 0:
            return jsonify({'error': f'Brak dostępnych egzemplarzy książki o ID: {book_id}'}), 400

        # Utworzenie wypożyczenia
        new_loan = Loan(
            book_id=book_id,
            borrower_id=borrower_id,
            loan_date=datetime.strptime(loan_date, '%Y-%m-%d'),
            return_date=datetime.strptime(return_date, '%Y-%m-%d'),
            status='Wypożyczona'
        )

        # Zaktualizowanie ilości dostępnych książek
        book.quantity -= 1
        book.status = 'Wypożyczona' if book.quantity == 0 else book.status

        loans.append(new_loan)
        db.session.add(new_loan)
        db.session.flush()

        new_history = LoanHistory(
            loan_id=new_loan.id,
            checkout_date=new_loan.loan_date,
            return_date=new_loan.return_date  # lub po prostu pominąć ten argument
        )
        db.session.add(new_history)

    db.session.add_all(loans)
    try:
        db.session.commit()
        loan_ids = [loan.id for loan in loans]
        return jsonify({'message': 'Książki wypożyczone pomyślnie', 'loan_ids': loan_ids}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@app.route('/api/loans', methods=['GET'])
def get_loans():
    loans = Loan.query \
        .join(Book, Loan.book_id == Book.id) \
        .join(Borrower, Loan.borrower_id == Borrower.id) \
        .all()

    loans_data = []
    for loan in loans:
        # Przykład, jak można połączyć tytuł książki i autorów
        book_authors = ', '.join([f"{author.first_name} {author.last_name}" for author in loan.book.authors])
        book_with_authors = f"{loan.book.title}-{book_authors}"

        loans_data.append({
            'id': loan.id,
            'book_title_with_authors': book_with_authors,
            'borrower_name': f"{loan.borrower.first_name} {loan.borrower.last_name}",
            'borrower_pesel': loan.borrower.pesel,
            'loan_date': loan.loan_date.strftime('%Y-%m-%d'),
            'return_date': loan.return_date.strftime('%Y-%m-%d') if loan.return_date else None,
            'status': loan.status
        })

    return jsonify(loans_data), 200


@app.route('/api/loans/return/<int:loan_id>', methods=['POST'])
def return_loan(loan_id):
    # Znalezienie wypożyczenia na podstawie loan_id
    loan = Loan.query.get_or_404(loan_id)

    # Znalezienie książki na podstawie book_id z wypożyczenia
    book = Book.query.get_or_404(loan.book_id)

    # Zwiększenie liczby dostępnych egzemplarzy książki
    book.quantity += 1
    book.status = 'Dostępna'

    # Aktualizacja historii wypożyczeń
    loan_history = LoanHistory.query.filter_by(loan_id=loan_id).first()
    if loan_history:
        loan_history.return_date = datetime.utcnow()  # Ustawienie aktualnej daty jako daty zwrotu
    else:
        # Jeśli w jakiś sposób nie ma wpisu w historii, tworzymy nowy
        new_history = LoanHistory(
            loan_id=loan_id,
            checkout_date=loan.loan_date,
            return_date=datetime.utcnow()  # Ustawienie aktualnej daty jako daty zwrotu
        )
        db.session.add(new_history)

    # Usunięcie rekordu wypożyczenia
    loan.status = 'Zwrócone'

    try:
        db.session.commit()
        return jsonify({'message': 'Książka zwrócona pomyślnie'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


def send_email_with_smtplib(recipient, subject, body):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = app.config['MAIL_USERNAME']
    msg['To'] = recipient

    with smtplib.SMTP_SSL(app.config['MAIL_SERVER'], app.config['MAIL_PORT']) as server:
        server.login(app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
        server.send_message(msg)


@app.route('/reset-password', methods=['POST'])
def reset_password():
    data = request.get_json()
    username = data.get('email')

    # Znajdowanie użytkownika po 'username', który faktycznie jest adresem email
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({'error': 'Nie znaleziono użytkownika z tym adresem email'}), 404

    # Generowanie bezpiecznego tokenu
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    token = serializer.dumps(username, salt=app.config['SECURITY_PASSWORD_SALT'])

    # Tworzenie linku do resetowania hasła
    reset_link = f"http://localhost:3000/reset/{token}"

    # Wysyłanie e-maila
    email_subject = "Resetowanie Hasła"
    email_body = f"Twój link do resetowania hasła: {reset_link}"
    send_email_with_smtplib(username, email_subject, email_body)

    return jsonify({'message': 'Link do resetowania hasła został wysłany na e-mail'}), 200


@app.route('/reset/<token>', methods=['POST'])
def reset_with_token(token):
    try:
        serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
        username = serializer.loads(token, salt=app.config['SECURITY_PASSWORD_SALT'], max_age=3600)
    except:
        return jsonify({'error': 'Nieprawidłowy lub przeterminowany link'}), 400

    data = request.get_json()
    new_password = data.get('password')

    # Tutaj powinieneś zaktualizować hasło w bazie danych
    user = User.query.filter_by(username=username).first()
    if user:
        user.set_password(new_password)
        db.session.commit()
        return jsonify({'message': 'Hasło zostało zresetowane'}), 200

    return jsonify({'error': 'Nie znaleziono użytkownika'}), 404


# Endpoint do pobierania szczegółów aktualnie zalogowanego użytkownika
@app.route('/api/user-details', methods=['GET'])
@jwt_required()
def get_user_details():
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user['username']).first()

    if not user:
        return jsonify({'error': 'Użytkownik nie znaleziony'}), 404

    role = Role.query.get(user.role_id)
    if not role:
        return jsonify({'error': 'Rola nie znaleziona'}), 404

    user_details = {
        'username': user.username,
        'role': 'Admin' if role.id == 1 else 'Pracownik'
    }

    if role.id != 1:  # Dodatkowe informacje dla pracowników
        employee = Employee.query.filter_by(user_id=user.id).first()
        if employee:
            user_details.update({
                'first_name': employee.first_name,
                'last_name': employee.last_name,
                'email': employee.email
            })

    return jsonify(user_details), 200


@app.route('/api/loan-history', methods=['GET'])
def get_loan_history():
    loan_histories = db.session.query(
        LoanHistory.id,
        Book.title,
        func.string_agg(Author.first_name + " " + Author.last_name, ', ').label('authors'),
        Borrower.first_name,
        Borrower.last_name,
        Borrower.pesel,
        LoanHistory.checkout_date,
        LoanHistory.return_date,
        Loan.status
    ).join(Loan, LoanHistory.loan_id == Loan.id) \
        .join(Book, Loan.book_id == Book.id) \
        .join(Borrower, Loan.borrower_id == Borrower.id) \
        .join(Author, Book.authors) \
        .group_by(LoanHistory.id, Book.id, Borrower.id, Loan.id) \
        .all()

    loan_history_data = []
    for history in loan_histories:
        book_with_authors = f"{history[1]} - {history[2]}"
        borrower_info = f"{history[3]} {history[4]} ({history[5]})"
        loan_date = history[6]
        return_date = history[7]
        status = history[8]

        # Sprawdzenie czy data zwrotu i data wypożyczenia są dostępne
        if status == 'Zwrócone' and return_date and loan_date:
            if (return_date - loan_date).days > 30:
                status = 'Przetrzymana'
        elif not return_date:
            status = 'Wypożyczona'

        loan_history_data.append({
            'id': history[0],
            'book_title_with_authors': book_with_authors,
            'borrower_info': borrower_info,
            'loan_date': loan_date.strftime('%Y-%m-%d'),
            'return_date': return_date.strftime('%Y-%m-%d') if return_date else '---',
            'status': status
        })

    return jsonify(loan_history_data), 200


@app.route('/api/loans/details/<int:loan_history_id>', methods=['GET'])
def get_loan_details(loan_history_id):
    loan_history = LoanHistory.query.get_or_404(loan_history_id)
    loan = Loan.query.get_or_404(loan_history.loan_id)

    if loan.book:
        book_authors = ', '.join([f"{author.first_name} {author.last_name}" for author in loan.book.authors])
        book_details = {
            'title': loan.book.title,
            'isbn': loan.book.isbn,
            'publisher': loan.book.publisher,
            'publication_year': loan.book.publication_year,
            'category': loan.book.category.name if loan.book.category else None,
            'authors': book_authors
        }
    else:
        book_details = {'title': 'Brak informacji o książce'}

    if loan.borrower:
        borrower_details = {
            'name': f"{loan.borrower.first_name} {loan.borrower.last_name}",
            'pesel': loan.borrower.pesel,
            'address': loan.borrower.address,
            'postal_code': loan.borrower.postal_code,
            'city': loan.borrower.city,
            'email': loan.borrower.email,
            'phone': loan.borrower.phone_number
        }
    else:
        borrower_details = {'name': 'Brak informacji o czytelniku'}

    return jsonify({'book': book_details, 'borrower': borrower_details})
