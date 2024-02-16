import os
from uuid import uuid4
from flask_login import current_user, login_required, login_user, logout_user
from app import create_app
from datetime import datetime, timezone
from database import db
from models import *
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from flask import flash, redirect, render_template, request, url_for

app = create_app()


@app.login_manager.user_loader
def user_loader(user_id):
    try:
        x = db.session.scalars(db.select(User).where(
            User.email == user_id)).one()
        return x
    except:
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
            try:
                sections = db.session.scalars(db.select(Section)).all()
                section_list = {}
                for s in sections:
                    section_list[s] = s.books
            except:
                section_list = {}
            return render_template('home.html', section_list=section_list)


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
                sections = db.session.scalars(db.select(Section)).all()
                section_list = {}
                for s in sections:
                    section_list[s] = s.books
            except:
                section_list = {}
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
    if request.method == 'POST':
        if not request.form['section_name'] or not request.form['description']:
            flash('Please enter all the fields', 'error')
        else:
            try:
                section = db.session.scalars(db.select(Section).where(
                    Section.section_name == request.form['section_name'])).one()
                flash("Section already exists", 'error')
            except:
                section = Section(
                    request.form['section_name'], request.form['description'], datetime.now(timezone.utc))
                db.session.add(section)
                db.session.commit()
                flash("Section was successfully added", 'success')
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
            flash('No Content Uploaded')
            return render_template('add_book.html')
        if 'cover' not in request.files:
            flash('No Cover Uploaded')
            return render_template('add_book.html')
        content = request.files['content']
        cover = request.files['cover']
        if content.filename == '':
            flash('No file selected for content')
            return render_template('add_book.html')
        if cover.filename == '':
            flash('No file selected for cover')
            return render_template('add_book.html')
        else:
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
            result = db.session.scalars(db.select(Book).where(Book.author.like(search))).all()
            print(result)

        if filter == 'name':
            result = db.session.scalars(db.select(Book).where(Book.book_name.like(search))).all()
            print(result)

        if filter == 'section':
            result = db.session.scalars(db.select(Section).where(Section.section_name.like(search))).all()
            print(result)

        return render_template('search_admin.html', result=result, filter=filter)

    if request.method == 'GET':
        user = current_user
        if user.role != 'admin':
            return render_template('error.html', message="Not Authorised")
        else:
            return render_template('search_admin.html', result=[])

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
            try:
                borrowing = db.session.scalars(db.select(Borrowing).where((Borrowing.book_id == book_id) & (Borrowing.user_id == user.user_id))).one()
                flag = True
                
            except Exception as e:
                print(e)
                flag = False
            return render_template('view_book.html', book=book, flag=flag)

@app.route('/borrowings', methods=['GET'])
@login_required
def borrowings():
    user = current_user
    if user.role != 'user':
        return render_template('error.html', message="Not Authorised")
    else:
        borrowings = db.session.execute(db.select(Borrowing, User, Book).join(User).join(Book).where(
            (Borrowing.user_id == user.user_id) & (Borrowing.book_id == Book.book_id))).all()
        print(borrowings)
        return render_template('borrowings.html', borrowings=borrowings)
    
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
        search_term = request.form["search_term"]
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
            result = db.session.scalars(db.select(Book).where(Book.author.like(search))).all()
            print(result)

        if filter == 'name':
            result = db.session.scalars(db.select(Book).where(Book.book_name.like(search))).all()
            print(result)

        if filter == 'section':
            result = db.session.scalars(db.select(Book).join(Section).where((Book.section_id == Section.section_id) & (Section.section_name.like(search)))).all()
            print(result)

        return render_template('search.html', result=result, filter=filter, search_term = search_term)

    if request.method == 'GET':
        user = current_user
        if user.role != 'user':
            return render_template('error.html', message="Not Authorised")
        else:
            return render_template('search.html', result=[])
