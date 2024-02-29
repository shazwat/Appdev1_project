import os
from uuid import uuid4
from flask_login import current_user, login_required, login_user, logout_user
from flask_restful import Resource, Api
from sqlalchemy import func
from sqlalchemy.exc import NoResultFound, SQLAlchemyError
from app import create_app
from datetime import datetime, timezone, timedelta
from database import db
from models import *
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from flask import flash, jsonify, make_response, redirect, render_template, request, url_for
# from email_validator import validate_email, EmailNotValidError
import matplotlib.pyplot as plt

ALLOWED_EXTENSIONS_COVER = {'png', 'jpg', 'jpeg'}
ALLOWED_EXTENSIONS_CONTENT = {'pdf'}

app = create_app()
api = Api(app, prefix="/api")


def allowed_file(filename, allowed_set):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_set
# API


class Books(Resource):
    def get(self, book_id):
        try:
            book = db.session.scalars(
                db.select(Book).where(Book.book_id == book_id)).one()
            return make_response(jsonify({"book_id": book.book_id,
                                          "book_name": book.book_name,
                                          "author": book.author,
                                          "content": book.content,
                                          "cover": book.cover,
                                          "price": book.price,
                                          "section": book.section.section_name}), 200)
        except:
            return make_response(jsonify("Book doesn't exist"), 404)

    def delete(self, book_id):
        try:
            book = db.session.scalars(
                db.select(Book).where(Book.book_id == book_id)).one()
            db.session.delete(book)
            db.session.commit()
            return make_response(jsonify("Book successfully deleted"), 200)
        except:
            return make_response(jsonify("Book doesn't exist"), 404)

    def put(self, book_id):
        try:
            book = db.session.scalars(
                db.select(Book).where(Book.book_id == book_id)).one()

            content = request.json

            if 'author' in content.keys() and isinstance(content['author'], str):
                book.author = content['author']

            if 'content' in content.keys() and isinstance(content['content'], str):
                book.content = content['content']

            if 'cover' in content.keys() and isinstance(content['cover'], str):
                book.cover = content['cover']

            if 'price' in content.keys() and isinstance(content['price'], int):
                book.price = content['price']

            if 'section_id' in content.keys() and isinstance(content['section_id'], int):
                book.section_id = content['section_id']

            db.session.commit()

            return make_response(jsonify({"book_id": book.book_id,
                                          "book_name": book.book_name,
                                          "author": book.author,
                                          "content": book.content,
                                          "cover": book.cover,
                                          "price": book.price,
                                          "section": book.section.section_name}), 200)

        except:
            return make_response(jsonify("Book doesn't exist"), 404)


class Bookslist(Resource):
    def get(self):
        books = db.session.scalars(db.select(Book)).all()
        books_list = {"books": []}
        for book in books:
            temp = {"book_id": book.book_id,
                    "book_name": book.book_name,
                    "author": book.author,
                    "content": book.content,
                    "cover": book.cover,
                    "price": book.price,
                    "section": book.section.section_name}
            books_list['books'].append(temp)
        return make_response(jsonify(books_list), 200)

    def post(self):
        payload = request.json
        try:
            book_name = payload['book_name']
            author = payload['author']
            content = payload['content']
            cover = payload['cover']
            price = payload['price']
            section_id = payload['section_id']
        except Exception:
            return make_response(jsonify('Incomplete post data'), 401)

        if not isinstance(book_name, str) or not isinstance(author, str) or not isinstance(content, str) or not isinstance(cover, str) or not isinstance(price, int) or not isinstance(section_id, int):
            return make_response(jsonify('Invalid post data'), 401)
        else:
            book = Book(book_name, author, content, cover, price, section_id)
            db.session.add(book)
            db.session.commit()
            return make_response(jsonify(book), 201)


class Sections(Resource):
    def get(self, section_id):
        try:
            section = db.session.scalars(db.select(Section).where(
                Section.section_id == section_id)).one()
            return make_response(jsonify({"section_id": section.section_id,
                                          "section_name": section.section_name,
                                          "description": section.description,
                                          "date_created": section.date_created}), 200)
        except:
            return make_response(jsonify("Section doesn't exist"), 404)

    def delete(self, section_id):
        try:
            section = db.session.scalars(db.select(Section).where(
                Section.section_id == section_id)).one()
            db.session.delete(section)
            db.session.commit()
            return make_response(jsonify("Section successfully deleted"), 200)
        except:
            return make_response(jsonify("Section doesn't exist"), 404)

    def put(self, section_id):
        try:
            section = db.session.scalars(db.select(Section).where(
                Section.section_id == section_id)).one()

            content = request.json

            if 'description' in content.keys() and isinstance(content['description'], str):
                section.description = content['description']

            if 'date_created' in content.keys() and isinstance(content['date_created'], str):
                section.date_created = content['date_created']

            db.session.commit()

            return make_response(jsonify({"section_id": section.section_id,
                                          "section_name": section.section_name,
                                          "description": section.description,
                                          "date_created": section.date_created}), 200)

        except:
            return make_response(jsonify("Section doesn't exist"), 404)


class Sectionslist(Resource):
    def get(self):
        sections = db.session.scalars(db.select(Section)).all()
        print(sections)
        sections_list = {"sections": []}
        for section in sections:
            temp = {"section_id": section.section_id,
                    "section_name": section.section_name,
                    "description": section.description,
                    "date_created": section.date_created}
            sections_list['sections'].append(temp)
        return make_response(jsonify(sections_list), 200)

    def post(self):
        payload = request.json
        try:
            section_name = payload['section_name']
            description = payload['description']
            date_created = payload['date_created']

        except Exception:
            return make_response(jsonify('Incomplete post data'), 401)

        if not isinstance(section_name, str) or not isinstance(description, str) or not isinstance(date_created, str):
            return make_response(jsonify('Invalid post data'), 401)
        else:
            try:
                section = db.session.scalars(db.select(Section).where(
                    Section.section_name == section_name)).one()
                return make_response(jsonify("A section with that name already exists"), 409)
            except:
                section = Section(section_name, description, date_created)
                db.session.add(section)
                db.session.commit()
                return make_response(jsonify({"section_id": section.section_id,
                                              "section_name": section.section_name,
                                              "description": section.description,
                                              "date_created": section.date_created}), 201)


api.add_resource(Sections, '/section/<int:section_id>')
api.add_resource(Sectionslist, '/sections/')

api.add_resource(Books, '/book/<int:book_id>')
api.add_resource(Bookslist, '/books/')


@app.login_manager.user_loader
def user_loader(user_id):
    try:
        user = db.session.query(User).filter(User.email == user_id).one()
        return user
    except NoResultFound:
        return None
    except Exception as e:
        app.logger.error(f"An error occurred while loading user : {e}")
        return None


@app.route('/home', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST':
        logout_user()
        return redirect(url_for('login'))
    if request.method == 'GET':
        user = current_user
        if user.role != 'user':
            return render_template('error.html', message="Not Authorised")
        else:
            section_list = {}
            latest_books = []
            try:
                sections = db.session.query(Section).all()
                for s in sections:
                    section_list[s] = s.books
            except SQLAlchemyError as e:
                section_list = {}
                print("Error loading sections and books: ", e)
            try:
                latest_books = db.session.query(Book).order_by(
                    Book.book_id.desc()).limit(5).all()
            except SQLAlchemyError as e:
                latest_books = []
                print("Error fetching latest books: ", e)

            return render_template('home.html', section_list=section_list, latest_books=latest_books)


@app.route('/home_admin', methods=['GET', 'POST'])
@login_required
def home_admin():
    if request.method == 'POST':
        logout_user()
        return redirect(url_for('login'))

    if request.method == 'GET':
        user = current_user
        if user.role != 'admin':
            return render_template('error.html', message="Not Authorised")
        else:
            try:
                sections = db.session.query(Section).all()
                section_list = {}
                for s in sections:
                    section_list[s] = s.books
            except SQLAlchemyError as e:
                section_list = {}
                app.logger.error(f"Error fetching sections: {str(e)}")

            return render_template('home_admin.html', section_list=section_list)


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if not request.form['email'] or not request.form['password']:
            flash('Please enter all the fields', 'error')
        else:
            try:
                user = db.session.scalars(db.select(User).where(
                    (User.email == request.form['email']) & (User.role == request.form['role']))).one()
                if check_password_hash(user.password, request.form['password']):
                    login_user(user)
                    if user.role == 'admin':
                        return redirect(url_for('home_admin'))
                    else:
                        return redirect(url_for('home'))
                else:
                    flash("Wrong password", "error")
            except:
                flash("User does not exist", "error")

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        if not request.form['name'] or not request.form['email'] or not request.form['password'] or not request.form['confirm_password']:
            flash('Please enter all the fields', 'error')
        elif request.form['password'] != request.form['confirm_password']:
            flash('The passwords do not match', 'error')
        else:
            try:
                user = db.session.scalars(db.select(User).where(
                    User.email == request.form['email'])).one()
                flash("An account with that email address is already present", "error")
            except:
                password = generate_password_hash(
                    request.form['password'], "sha256")
                user = User(
                    request.form['name'], request.form['role'], request.form['email'], password)
                if (request.form['role'] == 'admin'):
                    try:
                        user = db.session.scalars(db.select(User).where(
                            User.role == "admin")).one()
                        flash("An admin account is already present", "error")
                    except:
                        db.session.add(user)
                        db.session.commit()
                        flash('Admin account was successfully added', 'success')
                        return redirect(url_for('login'))
                else:
                    db.session.add(user)
                    db.session.commit()
                    flash('User account was successfully added', 'success')
                    return redirect(url_for('login'))

    return render_template('register.html')

# admin


@app.route('/add_section', methods=['GET', 'POST'])
@login_required
def add_section():
    if request.method == 'GET':
        user = current_user
        if user.role != 'admin':
            return render_template('error.html', message="Not Authorized")
        else:
            return render_template('add_section.html')

    elif request.method == 'POST':
        if not request.form['section_name'] or not request.form['description']:
            flash('Please enter all the fields', 'error')
            return render_template('add_section.html')

        try:
            section = db.session.scalars(db.select(Section).where(
                Section.section_name == request.form['section_name'])).one()

            flash("Section already exists", 'error')
        except:
            try:
                section = Section(
                    section_name=request.form['section_name'],
                    description=request.form['description'],
                    date_created=datetime.now(timezone.utc))

                db.session.add(section)
                db.session.commit()
                flash("Section was successfully added", 'success')
            except Exception as e:
                flash("Failed to add section: " + str(e), 'error')

        return render_template('add_section.html')


@app.route('/edit_section/<section_id>', methods=['GET', 'POST'])
@login_required
def edit_section(section_id):
    try:
        section = db.session.scalars(db.select(Section).where(
            Section.section_id == section_id)).one()
    except:
        flash("No Section is associated with that id", "error")
        return redirect(url_for('home_admin'))
    if request.method == 'GET':
        user = current_user
        if user.role != 'admin':
            return render_template('error.html', message="Not Authorized")
        else:
            return render_template('edit_section.html', section=section)
    if request.method == 'POST':
        if not request.form['section_name'] or not request.form['description']:
            flash('Please enter all the fields', 'error')
        else:
            section = db.session.scalars(db.select(Section).where(
                Section.section_id == section_id)).one()

            section.section_name = request.form['section_name']
            section.description = request.form['description']

            db.session.commit()
            flash("Section was successfully edited", 'success')
            return redirect(url_for('home_admin'))


@app.route('/delete_section/<section_id>', methods=['GET', 'POST'])
@login_required
def delete_section(section_id):
    try:
        section = db.session.scalars(db.select(Section).where(
            Section.section_id == section_id)).one()
    except:
        flash("No section is associated with that id", "error")
        return redirect(url_for('home_admin'))
    if request.method == 'GET':
        user = current_user
        if user.role != 'admin':
            return render_template('error.html', message="Not Authorised")
        else:
            return render_template('delete.html', message="Are you sure you want to delete the section?")
    if request.method == 'POST':
        if request.form['decision'] == 'yes':
            if section.books:
                flash(
                    f"{section.section_name} has books assigned to it and cannot be deleted.", "error")
                return redirect(url_for('home_admin'))
            else:
                db.session.delete(section)
                db.session.commit()
                flash('Section was successfully deleted', 'success')
                return redirect(url_for('home_admin'))
        else:
            return redirect(url_for('home_admin'))


@app.route('/add_book/<section_id>', methods=['GET', 'POST'])
@login_required
def add_book(section_id):
    try:
        section = db.session.scalars(db.select(Section).where(
            Section.section_id == section_id)).one()
    except:
        flash("Secion doesn't exist", 'error')
        return redirect(url_for('home_admin'))
    if request.method == 'GET':
        user = current_user
        if user.role != 'admin':
            return render_template('error.html', message="Unauthorized Access")
        else:
            return render_template('add_book.html')
    if request.method == 'POST':
        if not request.form['book_name'] or not request.form['author'] or not request.form['price']:
            flash('Please enter all fields', 'error')
            return render_template('add_book.html')
        if 'content' not in request.files:
            flash('No Content Uploaded', 'error')
            return render_template('add_book.html')
        if 'cover' not in request.files:
            flash('No Cover Uploaded', 'error')
            return render_template('add_book.html')
        content = request.files['content']
        cover = request.files['cover']
        if content.filename == '':
            flash('No file selected for content', 'error')
            return render_template('add_book.html')
        if cover.filename == '':
            flash('No file selected for cover', 'error')
            return render_template('add_book.html')
        if not allowed_file(content.filename, ALLOWED_EXTENSIONS_CONTENT):
            print('reached content')
            flash('Invalid File Type For Content', 'error')
            return render_template('add_book.html')

        if not allowed_file(cover.filename, ALLOWED_EXTENSIONS_COVER):
            print('reached cover')
            flash('Invalid File Type For Cover', 'error')
            return render_template('add_book.html')

        print(allowed_file(content.filename, ALLOWED_EXTENSIONS_CONTENT))
        print(allowed_file(cover.filename, ALLOWED_EXTENSIONS_COVER))
        print('reached else')
        content_filename = secure_filename(datetime.now().strftime(
            '%Y%m-%d%H-%M%S-') + str(uuid4()) + os.path.splitext(content.filename)[1])
        content.save(os.path.join(
            app.config['UPLOAD_FOLDER_CONTENT'], content_filename))
        cover_filename = secure_filename(datetime.now().strftime(
            '%Y%m-%d%H-%M%S-') + str(uuid4()) + os.path.splitext(cover.filename)[1])
        cover.save(os.path.join(
            app.config['UPLOAD_FOLDER_COVER'], cover_filename))

        book = Book(request.form['book_name'], request.form['author'],
                    content_filename, cover_filename, request.form['price'], section_id)
        db.session.add(book)
        db.session.commit()
        flash("Successfully added book", 'success')
        return redirect(url_for('home_admin'))


@app.route('/edit_book/<book_id>', methods=['GET', 'POST'])
@login_required
def edit_book(book_id):
    try:
        book = db.session.scalars(db.select(Book).where(
            Book.book_id == book_id)).one()
    except:
        flash("Book doesn't exist", 'error')
        return redirect(url_for('home_admin'))
    if request.method == 'GET':
        user = current_user
        if user.role != 'admin':
            return render_template('error.html', message="Unauthorized Access")
        else:
            return render_template('edit_book.html', book=book)
    if request.method == 'POST':
        if not request.form['book_name'] or not request.form['author'] or not request.form['price']:
            flash('Please enter all fields', 'error')
            return render_template('edit_book.html', book=book)
        if 'content' not in request.files:
            flash('No Content Uploaded')
            return render_template('edit_book.html', book=book)
        if 'cover' not in request.files:
            flash('No Cover Uploaded')
            return render_template('edit_book.html', book=book)
        content = request.files['content']
        cover = request.files['cover']
        content_filename = ''
        cover_filename = ''
        if content.filename != '':
            content_filename = secure_filename(datetime.now().strftime(
                '%Y%m-%d%H-%M%S-') + str(uuid4()) + os.path.splitext(content.filename)[1])
            content.save(os.path.join(
                app.config['UPLOAD_FOLDER_CONTENT'], content_filename))

        if cover.filename != '':
            cover_filename = secure_filename(datetime.now().strftime(
                '%Y%m-%d%H-%M%S-') + str(uuid4()) + os.path.splitext(cover.filename)[1])
            cover.save(os.path.join(
                app.config['UPLOAD_FOLDER_COVER'], cover_filename))

        if content_filename != '':
            book.content = content_filename
        if cover_filename != '':
            book.cover = cover_filename
        book.book_name = request.form['book_name']
        book.author = request.form['author']
        book.price = request.form['price']
        db.session.commit()
        flash("Successfully updated book", 'success')
        return redirect(url_for('home_admin'))


@app.route('/delete_book/<book_id>', methods=['GET', 'POST'])
@login_required
def delete_book(book_id):
    try:
        book = db.session.scalars(db.select(Book).where(
            Book.book_id == book_id)).one()
    except:
        flash("No book is associated with that id", "error")
        return redirect(url_for('home_admin'))
    if request.method == 'GET':
        user = current_user
        if user.role != 'admin':
            return render_template('error.html', message="Not Authorised")
        else:
            return render_template('delete.html', message="Are you sure you want to delete the book?")
    if request.method == 'POST':
        if request.form['decision'] == 'yes':
            db.session.delete(book)
            db.session.commit()

            flash('Book was successfully deleted', 'success')
            return redirect(url_for('home_admin'))
        else:
            return redirect(url_for('home_admin'))


@app.route('/borrow_requests', methods=['GET'])
@login_required
def borrow_requests():
    user = current_user
    if user.role != 'admin':
        return render_template('error.html', message="Not Authorised")
    else:
        borrowings = db.session.execute(db.select(Borrowing, User, Book).join(User).join(Book).where(
            (Borrowing.user_id == User.user_id) & (Borrowing.book_id == Book.book_id))).all()
        return render_template('borrow_requests.html', borrowings=borrowings)


@app.route('/borrow_requests/<borrowing_id>/<status>', methods=['POST'])
@login_required
def borrow_requests_status(borrowing_id, status):
    user = current_user
    if user.role != 'admin':
        return render_template('error.html', message="Not Authorised")
    else:
        borrowing = db.session.scalars(db.select(Borrowing).where(
            Borrowing.borrowing_id == borrowing_id)).one()
        borrowing.status = status
        db.session.commit()
        return redirect(url_for('borrow_requests'))


@app.route('/search_admin', methods=['GET', 'POST'])
@login_required
def search_admin():
    if request.method == 'POST':
        search_term = request.form["search_term"]
        if search_term == '':
            flash('Please type a search term', 'error')
            return render_template('search_admin.html', result=[])
        if 'filter' not in request.form:
            flash('Please choose a category to search in', 'error')
            return render_template('search_admin.html', result=[])
        filter = request.form['filter']
        search = "%{}%".format(search_term)
        result = []
        if filter == 'author':
            result = db.session.scalars(
                db.select(Book).where(Book.author.like(search))).all()
            print(result)

        if filter == 'name':
            result = db.session.scalars(db.select(Book).where(
                Book.book_name.like(search))).all()
            print(result)

        if filter == 'section':
            result = db.session.scalars(db.select(Section).where(
                Section.section_name.like(search))).all()
            print(result)

        return render_template('search_admin.html', result=result, filter=filter)

    if request.method == 'GET':
        user = current_user
        if user.role != 'admin':
            return render_template('error.html', message="Not Authorised")
        else:
            return render_template('search_admin.html', result=[])


@app.route('/summary', methods=['GET'])
@login_required
def summary():
    user = current_user
    if user.role != 'admin':
        return render_template('error.html', message="Not Authorized")
    else:
        books_request_section = db.session.query(Section.section_name, func.count(Borrowing.book_id).label('num_books_requested')) \
            .join(Book, Section.section_id == Book.section_id) \
            .join(Borrowing, Book.book_id == Borrowing.book_id) \
            .group_by(Section.section_name).all()

        books_per_section = db.session.query(Section.section_name, func.count(Book.book_id).label('num_books')) \
            .join(Book, Section.section_id == Book.section_id) \
            .group_by(Section.section_name) \
            .all()

        report_exists = False
        if books_request_section:
            sections = []
            num_books_requested = []
            for res in books_request_section:
                sections.append(res[0])
                num_books_requested.append(res[1])

        if books_per_section:
            sec = []
            num_of_books = []
            for result in books_per_section:
                sec.append(result[0])
                num_of_books.append(result[1])

        plt.figure(figsize=(8, 6))
        plt.barh(sections, num_books_requested, edgecolor='black')
        plt.xlim(0, max(num_books_requested) + 3)
        plt.ylabel('Sections')
        plt.xlabel('Number of books requested')
        plt.title('Number of books requested per Section', fontsize=18)
        plt.yticks(ha="right", fontsize=8)
        # plt.yticks(range(int(min(num_books_requested)), int(max(num_books_requested)) + 1))
        plt.tight_layout
        plt.savefig("./static/reports/summary_graph.png")

        plt.figure(figsize=(8, 6))
        plt.pie(num_of_books, labels=sec, autopct=lambda p: '{:.0f}'.format(
            p * sum(num_of_books) / 100), startangle=140, wedgeprops={'edgecolor': 'black', 'linewidth': 1.2})
        plt.title('Number of Books per Section', fontsize=18)
        plt.axis('equal')
        plt.tight_layout
        plt.savefig("./static/reports/pie_graph.png")
        report_exists = True

    return render_template('summary.html', report_exists=report_exists)

# USER CODE


@app.route('/view_book/<book_id>', methods=['GET', 'POST'])
@login_required
def view_book(book_id):
    try:
        book = db.session.scalars(
            db.select(Book).where(Book.book_id == book_id)).one()
    except Exception as e:
        print(e)
        flash("No book found", "error")
        return redirect(url_for('home'))

    if request.method == 'POST':
        user = current_user
        number_of_days = request.form['number_of_days']
        date_requested = datetime.now(timezone.utc)
        borrowing = Borrowing(user.user_id, book_id,
                              date_requested, number_of_days)
        db.session.add(borrowing)
        db.session.commit()
        flash("Book Request Submitted", 'success')
        return redirect(url_for('home'))

    if request.method == 'GET':
        user = current_user

        if user.role != 'user':
            return render_template('error.html', message="Not Authorised")
        else:
            flag = 'OK'
            rating = db.session.scalars(db.select(
                func.avg(Rating.rating)).where(Rating.book_id == book_id)).one()

            try:
                borrowing = db.session.scalars(db.select(Borrowing).where(
                    ((Borrowing.status == 'APPROVED') | (Borrowing.status == 'PENDING')) & (Borrowing.user_id == user.user_id))).all()
                if len(borrowing) == 5:
                    flag = 'MAXLIMIT'

            except Exception as e:
                print(e)

            try:
                borrowing = db.session.scalars(db.select(Borrowing).where(
                    (Borrowing.book_id == book_id) & (Borrowing.user_id == user.user_id) & (Borrowing.status == 'PENDING'))).one()
                flag = 'REQUESTED'

            except Exception as e:
                print(e)

            try:
                borrowing = db.session.scalars(db.select(Borrowing).where(
                    (Borrowing.book_id == book_id) & (Borrowing.user_id == user.user_id) & (Borrowing.status == 'APPROVED'))).one()
                flag = 'APPROVED'

            except Exception as e:
                print(e)

            return render_template('view_book.html', book=book, flag=flag, rating=rating)


@app.route('/borrowings', methods=['GET'])
@login_required
def borrowings():
    user = current_user
    if user.role != 'user':
        return render_template('error.html', message="Not Authorised")
    else:
        borrowings = db.session.execute(db.select(Borrowing, User, Book).join(User).join(Book).where(
            (Borrowing.user_id == user.user_id) & (Borrowing.book_id == Book.book_id))).all()

        for b in borrowings:

            if b[0].status == 'APPROVED' and (b[0].date_requested + timedelta(days=b[0].number_of_days)) <= datetime.utcnow():
                b[0].status = 'RETURNED'
                b[0].return_date = datetime.now(timezone.utc)
        db.session.commit()
        borrowings = db.session.execute(db.select(Borrowing, User, Book).join(User).join(Book).where(
            (Borrowing.user_id == user.user_id) & (Borrowing.book_id == Book.book_id))).all()
        return render_template('borrowings.html', borrowings=borrowings)


@app.route('/borrowings/<borrowing_id>', methods=['POST'])
@login_required
def borrowings_return(borrowing_id):
    borrowing = db.session.scalars(db.select(Borrowing).where(
        Borrowing.borrowing_id == borrowing_id)).one()
    borrowing.status = 'RETURNED'
    borrowing.return_date = datetime.now(timezone.utc)
    db.session.commit()
    return redirect(url_for('borrowings'))


@app.route('/view_borrowed_book/<book_id>', methods=['GET', 'POST'])
@login_required
def view_borrowed_book(book_id):
    try:
        book = db.session.scalars(
            db.select(Book).where(Book.book_id == book_id)).one()
    except Exception as e:
        flash("No book found", "error")
        return redirect(url_for('home'))

    if request.method == 'GET':
        user = current_user
        if user.role != 'user':
            return render_template('error.html', message="Not Authorised")
        else:
            return render_template('view_borrowed_book.html', book=book)


@app.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    if request.method == 'POST':
        search_term = request.form["search_term"].strip()
        if search_term == '':
            flash('Please type a search term', 'error')
            return render_template('search.html', result=[])
        if 'filter' not in request.form:
            flash('Please choose a category to search in', 'error')
            return render_template('search.html', result=[])
        filter = request.form['filter']
        search = "%{}%".format(search_term)
        result = []
        if filter == 'author':
            result = db.session.scalars(
                db.select(Book).where(Book.author.like(search))).all()
            print(result)

        if filter == 'name':
            result = db.session.scalars(db.select(Book).where(
                Book.book_name.like(search))).all()
            print(result)

        if filter == 'section':
            result = db.session.scalars(db.select(Book).join(Section).where(
                (Book.section_id == Section.section_id) & (Section.section_name.like(search)))).all()
            print(result)

        return render_template('search.html', result=result, filter=filter, search_term=search_term)

    if request.method == 'GET':
        user = current_user
        if user.role != 'user':
            return render_template('error.html', message="Not Authorised")
        else:
            return render_template('search.html', result=[])


@app.route('/rate_book/<book_id>', methods=['GET', 'POST'])
@login_required
def rate_book(book_id):
    try:
        book = db.session.scalars(
            db.select(Book).where(Book.book_id == book_id)).one()
    except:
        flash("No book is associated with that id", "error")
        return redirect(url_for('home'))
    if request.method == 'GET':
        user = current_user
        if user.role != 'user':
            return render_template('error.html', message="Not Authorised")
        else:
            try:
                db.session.scalars(db.select(Rating).where(
                    (Rating.user_id == user.user_id) & (Rating.book_id == book_id))).one()
                rate = False
            except Exception as e:
                rate = True
            return render_template('rating.html', book=book, rate=rate)

    if request.method == 'POST':
        user = current_user
        rating = request.form['rating']
        new_rating = Rating(book_id, user.user_id, rating)
        db.session.add(new_rating)
        db.session.commit()
        flash('Rating successfully recorded', 'success')
        return redirect(url_for('borrowings'))
