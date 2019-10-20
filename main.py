from flask import Flask, request, redirect, render_template, session
from flask_sqlalchemy import SQLAlchemy
import os
import jinja2


app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'f8wv3w2f>v9j4sEuhcNYydAGMzzZJgkGgyHE9gUqaJcCk^f*^o7fQyBT%XtTvcYM'


class Entry(db.Model):
  
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(180))
    body = db.Column(db.String(1000))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))


    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner
  
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    pw = db.Column(db.String(120))
    blogs = db.relationship('Entry', backref='owner')

    def __init__(self, username, pw):
        self.username = username
        self.pw = pw

@app.before_request
def require_login():
    allowed_routes = ['index', 'login', 'signup', 'display_blog_entries', 'index']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')


#login route
@app.route('/login', methods=['POST', 'GET'])
def login():
    username_error = ""
    pw_error = ""

    if request.method == 'POST':
        pw = request.form['pw']
        username = request.form['username']
        user = User.query.filter_by(username=username).first()

        if user and user.pw == pw:
            session['username'] = username
            return redirect('/newpost')
        if not user:
            return render_template('login.html', title="Login", username_error="Username does not exist.")
        else:
            return render_template('login.html',title="Login",  pw_error="Your username or password is incorrect.")
    
    return render_template('login.html',title="Login")

#signup route
@app.route("/signup", methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        pw = request.form['pw']
        confirm = request.form['confirm']
        taken = User.query.filter_by(username=username).first()

        username_error = ""
        pw_error = ""
        confirm_error = ""

        if username == "":
            username_error = "Please enter a username."
        elif len(username) <= 5 or len(username) > 20:
            username_error = "Username must be between 5 and 20 characters long."
        elif " " in username:
            username_error = "Username cannot contain any spaces."
        if pw == "":
            pw_error = "Please enter a password."
        elif len(pw) <= 3:
            pw_error = "Password must be greater than 3 characters long."
        if pw != confirm or confirm == "":
            confirm_error = "Passwords do not match."
        if taken:
            username_error = "Username already taken."
        if len(username) > 5 and len(pw) > 3 and pw == confirm and not taken:
            new_user = User(username, pw)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/newpost')
        else:
            return render_template('signup.html',
            username=username,
            username_error=username_error,
            pw_error=pw_error,
            confirm_error=confirm_error
            )

    return render_template('signup.html')
 
#
@app.route('/', methods=['POST', 'GET'])
def index():
    all_users = User.query.distinct()
    return render_template('index.html', title="Blog Users", list_all_users = all_users)
#
@app.route("/blog")
def display_blog_entries():
    post_id = request.args.get('id')
    single_user_id = request.args.get('owner_id')
    if (post_id):
        entry = Entry.query.get(post_id)
        return render_template('ind_entry.html', title="Blog Entry", entry=entry)
    else:
        if (single_user_id):
            ind_user_blog_posts = Entry.query.filter_by(owner_id=single_user_id)
            return render_template('singleuser.html', title="User Posts", posts=ind_user_blog_posts)
        else:
            all_blog_posts = Entry.query.all()
            return render_template('blog_list.html', title="Blog List", blog_list=all_blog_posts)
  
def is_valid(x):
        if x:
            return True
        else:
            return False

#newpost route
@app.route('/newpost', methods=['GET', 'POST'])
def new_entry():
    if request.method == 'POST':
        
        title_error = ""
        body_error = ""
        new_entry_title = request.form['title']
        new_entry_body = request.form['body']
        new_entry_owner = User.query.filter_by(username=session['username']).first()

        if is_valid(new_entry_title) and is_valid(new_entry_body):
            new_entry = Entry(new_entry_title, new_entry_body, new_entry_owner)
            db.session.add(new_entry)
            db.session.commit()
            url = "/blog?id=" + str(new_entry.id)
            return redirect(url)
        else:
            if not is_valid(new_entry_title) and not is_valid(new_entry_body):
                title_error = "Please enter text for blog title"
                body_error = "Please enter text for blog entry"
                return render_template('new_entry.html', body_error=body_error, title_error=title_error)
            elif not is_valid(new_entry_title):
                title_error = "Please enter text for blog title"
                return render_template('new_entry.html', title_error=title_error, new_entry_body=new_entry_body)
            elif not is_valid(new_entry_body):
                body_error = "Please enter text for blog entry"
                return render_template('new_entry.html', body_error=body_error, new_entry_title=new_entry_title)

    else: # GET
        return render_template('new_entry.html', title="New blog entry")

#logout
  
@app.route('/logout')
def logout():
    del session['username']
    return redirect('/')

if __name__ == '__main__':
    app.run()