from models import db
from flask import Flask
from flask_login import LoginManager


UPLOAD_FOLDER_COVER = './static/uploads/covers'
UPLOAD_FOLDER_CONTENT = './static/uploads/content'


def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.sqlite3'
    app.config['SECRET_KEY'] = "random string"
    app.config['UPLOAD_FOLDER_COVER'] = UPLOAD_FOLDER_COVER
    app.config['UPLOAD_FOLDER_CONTENT'] = UPLOAD_FOLDER_CONTENT

    db.app = app
    db.init_app(app)

    login_manager = LoginManager()
    login_manager.init_app(app)

    with app.app_context():
        db.create_all()

    return app


if __name__ == '__main__':
    app = create_app()
    from database import *
    from views import *
    app.run(debug=True, port=5000)
