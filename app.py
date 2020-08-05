from flask import Flask, render_template, redirect, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from models import connect_db, db, User
from forms import RegisterForm, LoginForm

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgres:///feedback_db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = "abc123"
app.config["DEBUG_TB_INTERCEPT_REDIRECTS"] = False

connect_db(app)
db.create_all()

toolbar = DebugToolbarExtension(app)

@app.route('/')
def show_homepage():
    return redirect('/register')

@app.route('/register', methods=["GET", "POST"])
def register_user():
    form = RegisterForm()

    if form.validate_on_submit():
        # Make a list of values from the form.data dict and splat them out into User.register instead of having to enter
        # every field's data one by one
        form_data = form.data
        form_data.pop('csrf_token')
        form_data = form_data
        form_data = [v for v in form_data.values()]

        new_user = User.register(*form_data)

        # Logic to check the errors.  If it's for both username and email, we want to display both error messages, if just one,
        # we want to display the correct error message for the correct field
        if type(new_user) == list:
            if len(new_user) == 2:
                form.username.errors = [new_user[0]]
                form.email.errors = [new_user[1]]
                # Notice we have to use render_template instead of redirect here, otherwise our errors won't show up
                # Don't fully understand yet why this happens
                return render_template('register.html', form=form)
            elif 'username' in new_user[0]:
                form.username.errors = [new_user[0]]
                return render_template('register.html', form=form)
            elif 'email' in new_user[0]:
                form.email.errors = [new_user[0]]
                return render_template('register.html', form=form)
        else:
            db.session.add(new_user)
            db.session.commit()

            session['username'] = new_user.username

            flash(f'Welcome, {new_user.first_name}!  Successfully created your account!', 'success')
            return redirect('/secret')

    return render_template('register.html', form=form)

@app.route('/login', methods=["GET", "POST"])
def login_user():
    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        pwd = form.password.data

        if User.authenticate(username, pwd):
            user = User.authenticate(username, pwd)

            session['username'] = user.username

            flash(f"Welcome back, {user.first_name}!", "success")
            return redirect('/secret')
        else:
            flash("Email and password don't match.", "danger")
            return redirect('/login')

    return render_template('login.html', form=form)

@app.route('/logout')
def logout_user():
    session.pop('username')
    flash('Successfully logged out.  Come back soon!', 'success')
    return redirect('/')

@app.route('/secret')
def show_secret():
    if 'username' in session:
        return render_template('secret.html')
    else:
        flash('Please sign in or sign up first!', 'danger')
        return redirect('/login')
