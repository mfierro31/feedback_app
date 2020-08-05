from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
bcrypt = Bcrypt()

def connect_db(app):
    """Connect to database"""
    db.app = app
    db.init_app(app)

class User(db.Model):
    """User model"""
    __tablename__ = 'users'

    username = db.Column(db.String(20), primary_key=True)
    password = db.Column(db.Text, nullable=False)
    email = db.Column(db.String(50), nullable=False, unique=True)
    first_name = db.Column(db.String(30), nullable=False)
    last_name = db.Column(db.String(30), nullable=False)

    @classmethod
    def register(cls, username, pwd, email, first, last):
        """Registers a user"""
        # check to see if username and email are unique
        if cls.query.filter_by(username=username).first() and cls.query.filter_by(email=email).first():
            return ["That username has already been taken.  Please choose another one.", "That email already has an account with us.  Please use another."]
        if cls.query.filter_by(username=username).first():
            return ["That username has already been taken.  Please choose another one."]
        if cls.query.filter_by(email=email).first():
            return ["That email already has an account with us.  Please use another."]

        hashed = bcrypt.generate_password_hash(pwd).decode('utf8')

        return cls(username=username, password=hashed, email=email, first_name=first, last_name=last)

    @classmethod
    def authenticate(cls, username, pwd):
        """Login a user"""
        user = cls.query.filter_by(username=username).first()

        # If there is a user by that username AND that user's unhashed password matches the password passed in...
        if user and bcrypt.check_password_hash(user.password, pwd):
            return user
        else:
            return False