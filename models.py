from sqlalchemy import ForeignKey
from database import db


class User(db.Model):
    user_id = db.Column('user_id', db.Integer, primary_key=True)
    user_name = db.Column(db.String(50))
    role = db.Column(db.String(50))
    email = db.Column(db.String(50))
    password = db.Column(db.String(50))
    authenticated = db.Column(db.Boolean, default=False)
    premium = db.Column(db.Boolean)

    def __init__(self, user_name, role, email, password, premium=False):
        self.user_name = user_name
        self.role = role
        self.email = email
        self.password = password
        self.premium = premium

    def is_active(self):
        return True

    def get_id(self):
        return self.email

    def is_authenticated(self):
        return self.authenticated

    def is_anonymous(self):
        return False


class Section(db.Model):
    section_id = db.Column('section_id', db.Integer, primary_key=True)
    section_name = db.Column(db.String(50))
    description = db.Column(db.String(50))
    date_created = db.Column(db.DateTime)
    books = db.relationship("Book", back_populates="section")

    def __init__(self, section_name, description, date_created):
        self.section_name = section_name
        self.description = description
        self.date_created = date_created


class Book(db.Model):
    book_id = db.Column('book_id', db.Integer, primary_key=True)
    book_name = db.Column(db.String(50))
    author = db.Column(db.String(6))
    content = db.Column(db.String(100))
    cover = db.Column(db.String(100))
    price = db.Column(db.Float)
    section_id = db.Column(ForeignKey(
        'section.section_id', ondelete="CASCADE"))
    section = db.relationship("Section", back_populates="books")

    def __init__(self, book_name, author, content, cover, price, section_id):
        self.book_name = book_name
        self.author = author
        self.cover = cover
        self.content = content
        self.price = price
        self.section_id = section_id


class Rating(db.Model):
    __tablename__ = 'ratings'
    book_id = db.Column(
        db.Integer,
        db.ForeignKey('book.book_id', ondelete="CASCADE"),
        primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('user.user_id', ondelete="CASCADE"),
        primary_key=True)
    rating = db.Column(
        db.Integer)

    def __init__(self, book_id, user_id, rating):
        self.book_id = book_id
        self.user_id = user_id
        self.rating = rating


class Borrowing(db.Model):
    __tablename__ = "borrowing"
    user_id = db.Column(db.Integer, db.ForeignKey(
        'user.user_id', ondelete="CASCADE"), primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey(
        'book.book_id', ondelete="CASCADE"), primary_key=True)
    date_issued = db.Column(db.DateTime)
    return_date = db.Column(db.DateTime)

    def __init__(self, user_id, book_id, date_issued, return_date):
        self.user_id = user_id
        self.book_id = book_id
        self.date_issued = date_issued
        self.return_date = return_date
