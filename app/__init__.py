from flask import Flask, request,render_template, redirect, flash, url_for, Blueprint
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_migrate import Migrate
from flask_moment import Moment
from flask_login import LoginManager, UserMixin, login_required, logout_user, current_user, login_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Mail, Message
from time import time
from smtplib import SMTP as SMTP 
from config import Config
from flask_mail import Mail
from flask_uploads import UploadSet, IMAGES, configure_uploads

#instantiate flask class
app = Flask(__name__)

app.config.from_object(Config)

#instantiate mail class
mail = Mail(app)

#creating db object
db = SQLAlchemy(app)
#createing migrate object
migrate = Migrate(app, db)
#createing moment object
moment = Moment(app)
#creating login object
login = LoginManager(app)
login.session_protection = 'strong'
login.login_view = 'login'
#creating images object
images = UploadSet('images', IMAGES)
configure_uploads(app, images)

#seperation of concerns
from app import routes, models, forms

