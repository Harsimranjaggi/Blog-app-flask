from werkzeug.utils import secure_filename
from app import app, db, lm
from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, logout_user, current_user
from datetime import datetime
import os

from app.models.tables import User, Post
from app.models.forms import LoginForm, RegisterForm, PostForm, EditForm

@lm.user_loader
def load_user(id):
    return User.query.filter_by(id=id).first()

@app.route("/")
def homepage():
    """Renders the homepage (`homepage.html`) displaying all blog posts.

    Guests can see all blog posts created by users, regardless of authentication status.
    """

    posts = Post.query.order_by(Post.date.desc()).all()  # Fetch all posts in descending order by date

    return render_template('homepage.html', posts=posts,profile=profile)

# @app.route("/index/")
@app.route("/index", methods=['GET','POST'])
def index():
    form_post = PostForm()
    if request.method == 'GET':
        if current_user.is_authenticated == True:
            posts = Post.query.filter_by(user_id=current_user.get_id()).order_by(Post.date.desc()).all()
            return render_template('index.html',form=form_post,posts=posts)
        else: 
            return redirect(url_for("login"))
        
    else:
        if form_post.validate_on_submit():
            id = current_user.get_id()
            user = User.query.filter_by(id=id).first()
            date = datetime.now().strftime('%d/%m/%Y %H:%M')
            NewPost = Post(content=form_post.content.data,title=form_post.title.data, date=date, user=user.name, nick=user.username, user_id=id)
            db.session.add(NewPost)
            db.session.commit()
            print(NewPost)
            return redirect(url_for("index"))
        else:
            return "ERRO!!"


@app.route("/login/", methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username = form.username.data).first()
        if user and user.password == form.password.data:
            login_user(user)
            flash("Logged in.")
            return redirect(url_for("index"))
        else:
            flash("Invalid login.")
    else:
        print(form.errors)
    return render_template('login.html', form=form)


@app.route('/logout/')
def logout():
    logout_user()
    flash("Logged out.")
    return redirect(url_for("homepage"))


@app.route('/register/', methods=["GET","POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        try:
            NewUserData = User(form.username.data,form.password.data,form.name.data,form.email.data)
            print(NewUserData)
            db.session.add(NewUserData)
            db.session.commit()
            return redirect(url_for("login"))
        except:
            return redirect(url_for("register"))
    else:
        print(form.errors)
    return render_template('register.html', form=form)


@app.route('/profile/<int:id>/')
def profile(id):
    if current_user.id == id:
        return redirect(url_for("my_profile"))
    else:
        posts = Post.query.filter_by(user_id=id).order_by(Post.date.desc()).all()
        user = User.query.filter_by(id=id).first()
        try:
            print(user.id) 
            if user.id != False:
                print('pagina do perfil ' + str(id))
                return render_template('profile.html', posts=posts,profile=user)
        except:
            return redirect(url_for("my_profile"))


@app.route('/profile/')
def my_profile():
    if current_user.is_authenticated == True:
        user = User.query.filter_by(id=current_user.id).first()
        posts = Post.query.filter_by(user_id=current_user.get_id()).order_by(Post.date.desc()).all()
        return render_template('my_profile.html', profile=user, posts=posts)
    else:
        redirect(url_for("login"))







def change_profile_pic_name(name):
    date = datetime.now().strftime('%d%m%Y%H%M%S')
    old_name = name.split(".")
    old_name[0] = "profile_pic" + str(date)
    new_name = '.'.join(old_name)
    return new_name

@app.route('/profile/change_image', methods=['POST'])
def profile_image():
    UPLOAD_FOLDER = os.path.join(os.getcwd(),str('app/static/images/' + str(current_user.get_id())))
    if UPLOAD_FOLDER == True:
        os.mkdir(UPLOAD_FOLDER)
    file = request.files['image']
    file.filename = change_profile_pic_name(file.filename)
    savePath = os.path.join(UPLOAD_FOLDER, secure_filename(file.filename))
    file.save(savePath)
    prof = User.query.filter_by(id=current_user.get_id()).first()
    prof.pic = str("/static/images/"+ str(current_user.get_id()) + '/' + str(file.filename)) 
    db.session.add(prof)
    db.session.commit()    
    print(prof.pic)
    return redirect(url_for("my_profile"))


@app.route('/search', methods=['POST'])
def search():
    search_data = request.form.get("search_data")
    search = "%{}%".format(search_data)
    posts = Post.query.filter(Post.title.like(search)).all()
    users = User.query.filter(User.name.like(search)).all()
    return render_template('search.html',users=users, posts=posts, search=search_data)

@app.route('/post/<int:id>/delete/', methods=['GET', 'POST'])
def delete_post(id):
  post = Post.query.get(id)
  db.session.delete(post)
  db.session.commit()
  flash("Post deleted successfully.")
  return redirect(url_for('index'))

  return render_template('index.html', post=post)

@app.route('/post/<int:id>/edit/', methods=['GET', 'POST'])
def edit_post(id):
  post = Post.query.get(id)



  # Handle GET request: Render edit form with pre-filled data
  if request.method == 'GET':
    form = PostForm()  # Assuming you have a PostForm for editing posts
    form.title.data = post.title
    form.content.data = post.content
    return render_template('edit.html', form=form, post=post)

  # Handle POST request: Process form data and update post
  if request.method == 'POST':
    form = PostForm()
    if form.validate_on_submit():
      post.title = form.title.data
      post.content = form.content.data
      db.session.commit()
      flash("Post edited successfully.")
      return redirect(url_for('index'))  # Or redirect to specific post after edit
    else:
      return render_template('edit.html', form=form, post=post)

  return render_template('edit.html', post=post)  # Shouldn't reach here




