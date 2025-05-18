from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from hangman.config import Config
from apscheduler.schedulers.background import BackgroundScheduler

scheduler=BackgroundScheduler()
db=SQLAlchemy()
bcrypt=Bcrypt()
login_manager=LoginManager()
login_manager.login_view='user.login'
login_manager.login_message_category='info'

from hangman.utils import reset_mail, confirmation_mail
from hangman.routes import user
def create_app():
    app=Flask(__name__)
    app.config.from_object(Config) 
    scheduler.start()
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    confirmation_mail.init_app(app)
    reset_mail.init_app(app)
    app.register_blueprint(user)
    return app
