from flask import send_from_directory, abort, request,render_template, redirect, flash, url_for, Blueprint
from app import app
from app.forms import LoginForm, EditPostForm, ContactForm, SearchForm, RegisterationForm, PostForm, CommentForm, ResetPasswordForm, ResetPasswordRequestForm
from flask_login import LoginManager, UserMixin, login_required, logout_user, current_user, login_user
from werkzeug.urls import url_parse
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import User, Post, Comment
from datetime import datetime
from app import db, images
import jwt
from flask_mail import Message
from app import mail
from werkzeug.utils import secure_filename

#index endpoit
@app.route("/")
def index():
    return render_template("index.html")

# endpoint to post a blog
@app.route("/add_blog")
@login_required
def add_blog():
    form = PostForm()
    return render_template("add_blog.html", form=form)

#blogs endpoint
@app.route("/blogs", methods=["GET", "POST"])
def blogs():
    form = PostForm()
    if request.method == "POST":
        #creating an object to save the image
        filename = images.save(request.files["image"])
        url = images.url(filename)
        #posting data to database
        post = Post(title=form.title.data,author=form.author.data.title(),content=form.content.data, image_filename=filename,image_url=url, date_posted=datetime.utcnow())
        db.session.add(post)
        db.session.commit()
        flash('Your blog has been added successfully', 'success')

    form = SearchForm()
    #querying data from database and managing blogs pagination
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('blogs', page=posts.next_num) if posts.has_next else None
    prev_url = url_for('blogs', page=posts.prev_num)  if posts.has_prev else None
    return render_template("blogs.html", form=form, posts=posts.items, next_url=next_url, prev_url=prev_url)

#endpoint to search for a particular blogs keyword(title or author)
@app.route('/search')
def search():
    form = SearchForm()
    query = request.args.get('search')
    posts = Post.query.whoosh_search(query, limit=5).all()
    return render_template("blogs.html",form=form, posts=posts)

#the about endpoint
@app.route("/about")
def about():
    return render_template("about.html")

#the login endpoint
@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if request.method == "POST":
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember_me.data)
                # return to attemted protected routes after successfully logged in
                next_page = request.args.get("next")
                return redirect(next_page or url_for('dashboard'))
            flash("Invalid email or password", "info")
            return render_template("login.html", form=form)
        flash("Invalid email or password", "danger")
        return render_template("login.html", form=form)
    return render_template("login.html", form=form)    

#the register endpoint
@app.route("/register", methods=["GET", "POST"])
def sign_up():
    form = RegisterationForm(request.form)
    if request.method == "POST":
        #create an object and pass the hashed password
        hashed_password = generate_password_hash(form.password.data, method="sha256")
        data = User.query.filter_by(email=form.email.data).first()
        if data:
            #check if email alredy in the database
            if data.email == form.email.data:
                flash("User already exist", "danger")
                return render_template("register.html", form=form)
        user = User(username=form.username.data, email=form.email.data, password=hashed_password, date_registered=datetime.utcnow())
        #because only admin can register, check if email matches with admin email
        if form.email.data == app.config['ADMIN']:
            db.session.add(user)
            db.session.commit()
            flash("Successfully registered ", "success")
            return redirect(url_for("login"))
        flash("this is a personal blog, you are not allow to signup", "info")
        return render_template("register.html", form=form)
        
    return render_template("register.html", form=form)

#endpoint to a single blog   
@app.route("/post/<int:post_id>", methods=["GET", "POST"])
def post(post_id):
    post = Post.query.get_or_404(post_id)
    page = request.args.get('page', 1, type=int)
    comments = Comment.query.order_by(Comment.date_commented.desc()).paginate(page, app.config['COMMENTS_PER_PAGE'], False)
    next_url = url_for('post', post_id=post.id, page=comments.next_num) if comments.has_next else None
    prev_url = url_for('post', post_id=post.id, page=comments.prev_num)  if comments.has_prev else None
    #blog views
    post.views += 1
    db.session.commit()

    #comment to a parcular blog
    form = CommentForm(request.form)
    if request.method == "POST":
        comment = Comment(name=form.name.data, content=form.content.data, date_commented=datetime.utcnow())#, post_id=post.id)
        db.session.add(comment)
        post.commentts += 1
        db.session.commit()
        return redirect(request.url)
    return render_template("post.html", post=post, form=form, comments=comments.items, next_url=next_url, prev_url=prev_url)

#dashboard endpoint
@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")

#func with flask-mail class Message passing to msg object
def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    mail.send(msg)
    return 'Message has been sent to your email'

#helper func password reset
def send_password_reset_email(user):
    token = user.get_reset_password_token()
    send_email('Reset Your Password',sender=app.config['ADMIN'][0],recipients=[user.email],text_body=render_template('resets_password.txt', user=user, token=token),html_body=render_template('resets_password.html', user=user, token=token))


#reset_password_request endpoint
@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    form = ResetPasswordRequestForm(request.form)
    if request.method == "POST":
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('Check your email for the instructions to reset your password')
        return redirect(url_for('login'))
    return render_template('reset_password_request.html', title='Reset Password', form=form)

#reset_password endpoint
@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('index'))
    form = ResetPasswordForm(request.form)
    if request.method == "POST":
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)

#the contact endpoint
@app.route("/contact", methods=['GET','POST'])
def contact():
    form = ContactForm()
    if request.method == "POST":
        #sending contact email MGS 
        msg = Message(subject=form.subject.data, sender=form.email.data,recipients=['kimkazong@gmail.com'])
        msg.body = """
        From: %s , 
        Email: <%s>
        %s
        """ % (form.name.data.upper(), form.email.data, form.message.data)
        mail.send(msg)
        flash("Your email has been sent MGS", "success")
        return redirect(request.url)
    return render_template("contact.html", form=form)

@app.route("/post/<int:post_id>/update", methods=['GET','POST'])
@login_required
def update_blog(post_id):
    post = Post.query.get_or_404(post_id)
    form = EditPostForm()
    if request.method == "POST":
        post.title = form.title.data
        post.author = form.author.data
        post.content = form.content.data
        db.session.commit()
        flash("Blog updated", "success")
        return redirect(url_for("post", post_id=post.id))
    elif request.method == "GET":
        #populating the fields with the query data from database
        form.title.data = post.title
        form.author.data = post.author
        form.content.data = post.content
        
    return render_template("blog.html", form=form, post=post)

@app.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_blog(post_id):
    post = Post.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    flash("Blog deleted", "success")
    return redirect(url_for("blogs"))

#logging out endpoint
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You are now logged out', "success")
    return redirect(url_for('login'))

