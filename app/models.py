# Modele definiują strukturę tabel w bazie danych oraz relacje między nimi.
from app import db


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    user_type = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(255), nullable=False)

    # Relacje
    loans = db.relationship('Loan', backref='user', lazy='dynamic')

    # Dodatkowe metody, walidatory


class Book(db.Model):
    __tablename__ = 'books'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    author = db.Column(db.String(255), nullable=False)
    publication_year = db.Column(db.Integer)
    status = db.Column(db.String(50), nullable=False, default='available')

    # Relacje
    loans = db.relationship('Loan', backref='book', lazy=True)


class Loan(db.Model):
    __tablename__ = 'loans'
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    loan_date = db.Column(db.Date, nullable=False)
    return_date = db.Column(db.Date)


class Review(db.Model):
    __tablename__ = 'reviews'
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text)

    # Relacje
    user = db.relationship('User', backref=db.backref('reviews', lazy=True))
    book = db.relationship('Book', backref=db.backref('reviews', lazy=True))
