from flask_wtf import Form
from wtforms import MultipleFileField, StringField,BooleanField, TextAreaField,PasswordField, validators, SubmitField, ValidationError
from flask_wtf.file import  FileField, FileAllowed, file_required, FileRequired
from app.__init__ import images

#user form
class RegisterationForm(Form):
    username = StringField(u'Username', validators=[validators.input_required(), validators.Length(min=1, max=50)])
    email = StringField(u'Email', validators=[validators.input_required(), validators.Email()])
    password = PasswordField('Password', [validators.DataRequired(), validators.EqualTo('confirm', message='password do not match')])
    confirm = PasswordField('Confirm password')

#login form
class LoginForm(Form):
    email = StringField('Email', validators=[validators.input_required(), validators.Email()])
    password = PasswordField('Password', [validators.DataRequired()])
    remember_me = BooleanField('Keep me logged in')

#posting form
class PostForm(Form):
    title = StringField(u'Title', validators=[validators.input_required(), validators.Length(min=1, max=50)])
    author = StringField(u'Author', validators=[validators.input_required(), validators.Length(min=1, max=50)])
    content = TextAreaField(u'Content', validators=[validators.input_required()])
    image = MultipleFileField(u'Photo', validators=[FileRequired(), FileAllowed(images, 'Image only!')])

class EditPostForm(Form):
    title = StringField(u'Title', validators=[validators.input_required(), validators.Length(min=1, max=50)])
    author = StringField(u'Author', validators=[validators.input_required(), validators.Length(min=1, max=50)])
    content = TextAreaField(u'Content', validators=[validators.input_required()])
    

#comments form
class CommentForm(Form):
    name = StringField(u'Name', validators=[validators.input_required()])
    content = TextAreaField(u'Content', validators=[validators.input_required()])

#reset password request form
class ResetPasswordRequestForm(Form):
    email = StringField('Email', validators=[validators.input_required(), validators.Email()])
    submit = SubmitField('Request Password Reset')

#reset password form
class ResetPasswordForm(Form):
    password = PasswordField('Password', validators=[validators.input_required()])
    password2 = PasswordField('Repeat Password', validators=[validators.input_required(), validators.EqualTo('password')])
    submit = SubmitField('Request Password Reset')

#search form
class SearchForm(Form):
    search = StringField(u'search', validators=[validators.input_required()])

#contact form
class ContactForm(Form):
    message = TextAreaField(u'Enter Message', validators=[validators.input_required()])
    name = StringField(u'Write your name', validators=[validators.input_required()])
    email = StringField(u'Email', validators=[validators.input_required(), validators.Email()])
    subject = StringField(u'Enter subject', validators=[validators.input_required()])
    
