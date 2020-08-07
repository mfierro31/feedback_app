from flask import Flask, render_template, redirect, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from models import connect_db, db, User, Feedback
from forms import RegisterForm, LoginForm, FeedbackForm

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
    if 'username' in session:
        user = User.query.get_or_404(session['username'])
        return render_template('home.html', user=user)

    return render_template('home.html')

@app.route('/users')
def show_users():
    if 'username' in session:
        users = User.query.all()
        return render_template('users.html', users=users)
    else:
        flash('You have to either log in or sign up to view users!', 'danger')
        return redirect('/login')

@app.route('/register', methods=["GET", "POST"])
def register_user():
    form = RegisterForm()

    if 'username' in session:
        flash('Please log out first if you want to create another account.', 'warning')
        return redirect(f"/users/{session['username']}")

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
                # This is because with redirect, you can't pass in the form to it.  And since errors are located in form, they
                # don't show up
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
            return redirect(f'/users/{new_user.username}')

    return render_template('register.html', form=form)

@app.route('/login', methods=["GET", "POST"])
def login_user():
    form = LoginForm()

    if 'username' in session:
        flash("You're already logged in!", "danger")
        return redirect(f"/users/{session['username']}")

    if form.validate_on_submit():
        username = form.username.data
        pwd = form.password.data

        if User.authenticate(username, pwd):
            user = User.authenticate(username, pwd)

            session['username'] = user.username

            flash(f"Welcome back, {user.first_name}!", "success")
            return redirect(f'/users/{user.username}')
        else:
            flash("Email and password don't match.", "danger")
            return redirect('/login')

    return render_template('login.html', form=form)

@app.route('/logout')
def logout_user():
    if 'username' not in session:
        flash("You're already logged out!", "danger")
        return redirect('/')
        
    session.pop('username')
    flash('Successfully logged out.  Come back soon!', 'success')
    return redirect('/')

@app.route('/users/<username>')
def show_user(username):
    user = User.query.get_or_404(username)

    if 'username' in session:
        return render_template('user.html', user=user)
    else:
        flash('Please log in or sign up first!', 'danger')
        return redirect('/login')

@app.route('/users/<username>/delete', methods=["POST"])
def delete_user(username):
    user = User.query.get_or_404(username)

    if session.get('username') == user.username:
        db.session.delete(user)
        db.session.commit()

        session.pop('username')

        flash('Successfully deleted your account.', 'success')
        return redirect('/')
    else:
        if 'username' in session:
            flash("You can't delete that user!  You can only delete your own profile!", "danger")
            return redirect(f"/users/{session['username']}")
        else:
            flash("You can't delete that user!  Log in or sign up to delete your own profile.", "danger")
            return redirect('/login')

@app.route('/users/<username>/feedback/add', methods=["GET", "POST"])
def add_feedback(username):
    form = FeedbackForm()
    user = User.query.get_or_404(username)

    if session.get('username') == user.username:
        if form.validate_on_submit():
            title = form.title.data
            content = form.content.data

            new_feedback = Feedback(title=title, content=content, username=user.username)

            db.session.add(new_feedback)
            db.session.commit()

            flash(f'Successfully added your feedback.  Thanks, {user.first_name}!', 'success')
            return redirect(f'/users/{user.username}')
    else:
        if 'username' in session:
            flash("You can't add feedback for another user!  Add your own!", "danger")
            return redirect(f"/users/{session['username']}")
        else:
            flash("You can't add feedback for another user!  Log in or sign up to add your own.", "danger")
            return redirect('/login')

    return render_template('feedback-form.html', form=form, user=user)

@app.route('/feedback/<int:feedback_id>/update', methods=["GET", "POST"])
def edit_feedback(feedback_id):
    feedback = Feedback.query.get_or_404(feedback_id)
    form = FeedbackForm(obj=feedback)

    if feedback.user.username == session.get('username'):
        if form.validate_on_submit():
            feedback.title = form.title.data
            feedback.content = form.content.data

            db.session.commit()

            flash('Successfully edited your feedback!', 'success')
            return redirect(f'/users/{feedback.user.username}')
    else:
        if 'username' in session:
            flash("You can't edit this user's feedback!  Edit your own!", "danger")
            return redirect(f"/users/{session['username']}")
        else:
            flash("You can't edit this user's feedback!  Log in or sign up to edit your own!", "danger")
            return redirect('/login')
        
    return render_template('edit-feedback.html', feedback=feedback, form=form)

@app.route('/feedback/<int:feedback_id>/delete', methods=["POST"])
def delete_feedback(feedback_id):
    feedback = Feedback.query.get_or_404(feedback_id)

    if feedback.user.username == session.get('username'):
        db.session.delete(feedback)
        db.session.commit()

        flash('Successfully deleted your feedback', 'success')
        return redirect(f'/users/{feedback.user.username}')
    else:
        if 'username' in session:
            flash("You can't delete this user's feedback!  You can only delete your own!", "danger")
            return redirect(f'/users/{feedback.user.username}')
        else:
            flash("You can't delete this user's feedback!  Log in or sign up to delete your own.", "danger")
            return redirect('/login')

@app.route('/feedback')
def show_all_feedback():
    feedback = Feedback.query.all()

    if 'username' in session:
        user = User.query.get_or_404(session['username'])
        return render_template('feedback.html', feedback=feedback, user=user)
    else:
        flash("Please log in or sign up first!", "danger")
        return redirect('/login')