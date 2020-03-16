from flask_login import  UserMixin
from app import db
from app import login
import jwt
from time import time
from app import app

import flask_whooshalchemy as wa

#user model
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(300), nullable=False)
    date_registered = db.Column(db.DateTime) 
    posts  = db.relationship('Post', backref=db.backref('users'), lazy=True)
    comments  = db.relationship('Comment', backref=db.backref('users'), lazy=True)
    #constructor
    def __init__(self, username, email, password, date_registered):
        self.username = username
        self.email = email
        self.password = password
        self.date_registered = date_registered
    
    @login.user_loader
    def load_user(id):
        return User.query.get(id)

    #generate password token
    def get_reset_password_token(self, expires_in=600):
        return jwt.encode({'reset_password': self.id, 'exp': time() + expires_in}, app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)

#post model
class Post(db.Model):
    __tablename__ = 'posts'
    __searchable__ = ['title', 'author'] #search by keywords(title or author)
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(100),nullable=False)
    author = db.Column(db.String(50),nullable=False)
    content = db.Column(db.Text, nullable=False)
    image_filename = db.Column(db.String, default=None, nullable=True)
    image_url = db.Column(db.String, default=None, nullable=True)
    date_posted = db.Column(db.DateTime)
    commentts= db.Column(db.Integer, default=0)
    views = db.Column(db.Integer, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    comments  = db.relationship('Comment', backref=db.backref('posts', lazy=True))
    #constructor
    def __init__(self, title, author, content, image_filename, image_url, date_posted):
        self.title = title
        self.author = author
        self.content = content
        self.image_filename = image_filename
        self.image_url = image_url
        self.date_posted = date_posted   


wa.whoosh_index(app, Post)

#comment model
class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(50),nullable=False)
    content = db.Column(db.Text, nullable=False)
    date_commented = db.Column(db.DateTime)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    #constructor
    def __init__(self, name, content, date_commented):#, post_id):
        self.name = name
        self.content = content
        self.date_commented = date_commented 
        #self.post_id = post_id
         
#programmatic creating database
db.create_all()

