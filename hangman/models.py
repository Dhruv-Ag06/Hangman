from hangman import db,login_manager
from flask import current_app
from flask_login import  UserMixin
from itsdangerous import URLSafeTimedSerializer as Serializer
from datetime import datetime

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model,UserMixin):
    __bind_key__='db1'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password=db.Column(db.String(60),nullable=False)
    picture=db.Column(db.String(20),nullable=False,default='default.jpg')
    games = db.relationship('Game', backref='player', lazy=True)

    def get_reset_token(self):
        s = Serializer(current_app.config['SECRET_KEY'])
        return s.dumps({'user_id': self.id})
    
    @staticmethod
    def verify_reset_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token,max_age=1800)['user_id']
        except:
            return None
        return User.query.get(user_id)
    
    def __repr__(self):
        return f"User('{self.username}', '{self.email}',{self.password})"
    
class Game(db.Model):
    __bind_key__='db1'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    word = db.Column(db.String(100), nullable=False)
    date_played=db.Column(db.DateTime,nullable=False,default=datetime.utcnow)
    status=db.Column(db.String(5),nullable=False,default="lost")
    def __repr__(self):
        return f"Game('{self.date_played}', '{self.word}', '{self.status}')"

class Unauthenticated_User(db.Model,UserMixin):
    __bind_key__="db2"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password=db.Column(db.String(60),nullable=False)
    created_at=db.Column(db.DateTime,default=datetime.utcnow)

    def get_confirmation_token(self):
        s = Serializer(current_app.config['SECRET_KEY'],expires_in=1800)
        return s.dumps({'unauthenticated_user_email': self.email})
    
    @staticmethod
    def verify_confirmation_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_email = s.loads(token,max_age=1800)['unauthenticated_user_email']
            return user_email
        except:
            return None
        
    
    def __repr__(self):
        return f"User('{self.username}', '{self.email}',{self.password})"
