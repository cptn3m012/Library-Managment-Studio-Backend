# Modele definiują strukturę tabel w bazie danych oraz relacje między nimi
from datetime import datetime
from app import db
from werkzeug.security import generate_password_hash, check_password_hash


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    role_name = db.Column(db.String(255), nullable=False)

    # Relacje
    users = db.relationship('User', backref='role', lazy=True)


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    # Relacje
    employees = db.relationship('Employee', backref='user', lazy=True)
    notifications = db.relationship('Notification', backref='user', lazy=True)
    reports = db.relationship('Report', backref='user', lazy=True)

    # Metody
    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)


class Employee(db.Model):
    __tablename__ = 'employees'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    first_name = db.Column(db.String(255), nullable=False, index=True)
    last_name = db.Column(db.String(255), nullable=False, index=True)
    email = db.Column(db.String(255))
    phone_number = db.Column(db.String(20))
    pesel = db.Column(db.String(11), unique=True, nullable=False)
    hired_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relacje
    loans = db.relationship('Loan', backref='employee', lazy=True)


class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)

    # Relacje
    books = db.relationship('Book', backref='category', lazy=True)


class Author(db.Model):
    __tablename__ = 'authors'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(255), nullable=False)
    last_name = db.Column(db.String(255), nullable=False)


# Tabela asocjacyjna dla relacji książka-autor
book_author = db.Table('book_author',
                       db.Column('book_id', db.Integer, db.ForeignKey('books.id'), primary_key=True),
                       db.Column('author_id', db.Integer, db.ForeignKey('authors.id'), primary_key=True)
                       )


class Book(db.Model):
    __tablename__ = 'books'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False, index=True)
    isbn = db.Column(db.String(20), index=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    status = db.Column(db.String(50), default='Dostępna')
    publication_year = db.Column(db.Integer)
    publisher = db.Column(db.String(255))
    quantity = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relacje
    loans = db.relationship('Loan', backref='book', lazy=True)
    reservations = db.relationship('Reservation', backref='book', lazy=True)
    # Relacja wielu-do-wielu z Author
    authors = db.relationship('Author', secondary=book_author, backref=db.backref('books', lazy='dynamic'))


class Borrower(db.Model):
    __tablename__ = 'borrowers'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(255), nullable=False, index=True)
    last_name = db.Column(db.String(255), nullable=False, index=True)
    email = db.Column(db.String(255))
    phone_number = db.Column(db.String(20))
    pesel = db.Column(db.String(11), unique=True, nullable=False)
    address = db.Column(db.String(255), nullable=False)
    postal_code = db.Column(db.String(10), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relacje
    loans = db.relationship('Loan', backref='borrower', lazy=True)
    reservations = db.relationship('Reservation', backref='borrower', lazy=True)


class Loan(db.Model):
    __tablename__ = 'loans'
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'))
    borrower_id = db.Column(db.Integer, db.ForeignKey('borrowers.id'))
    loan_date = db.Column(db.DateTime, nullable=False)
    return_date = db.Column(db.DateTime)
    status = db.Column(db.String(50), default='Wypożyczona')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class LoanHistory(db.Model):
    __tablename__ = 'loan_history'
    id = db.Column(db.Integer, primary_key=True)
    loan_id = db.Column(db.Integer, db.ForeignKey('loans.id'))
    checkout_date = db.Column(db.DateTime, nullable=False)
    return_date = db.Column(db.DateTime, nullable=False)
