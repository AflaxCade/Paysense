from datetime import datetime
from app import db, login_manager, app
from flask_login import UserMixin
from itsdangerous import URLSafeTimedSerializer as Serializer


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# This code defines the User model, representing a User in the database.
class User(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    usertype = db.Column(db.String(10), nullable=False)
    profile_pic = db.Column(db.String(20), nullable=False, default='default.jpg')
    reg_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    accounts = db.relationship('Account', backref='owner', lazy=True)


    def get_reset_token(self):
        s = Serializer(app.config['SECRET_KEY'])
        return s.dumps({'user_id': self.id})

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token, max_age=120)['user_id']
        except:
            return None
        return User.query.get(user_id)

    # The __repr__() method is defined to provide a string representation of a User instance.
    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.profile_pic}')"


# This code defines the Account model, representing an account in the database.
class Account(db.Model):
    account_number = db.Column(db.Integer, primary_key=True)
    account_name = db.Column(db.String(50), nullable=False)
    balance = db.Column(db.Numeric(10, 2), nullable=False)
    reg_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    transactions = db.relationship('Transaction', backref='account', lazy=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'),nullable=False)

    # The __repr__() method is defined to provide a string representation of an Account instance.
    def __repr__(self):
        return f"Account('{self.account_name}', '{self.balance}', '{self.reg_date}')"


# This code defines the Transaction model, representing a transaction in the database.
class Transaction(db.Model):
    transaction_id = db.Column(db.Integer, primary_key=True)
    account_number = db.Column(db.Integer, db.ForeignKey('account.account_number'),nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    description = db.Column(db.Text, nullable=False)
    transaction_type = db.Column(db.String(20))
    date = db.Column(db.DateTime, nullable=False)

    # The __repr__() method is defined to provide a string representation of an Transaction instance.
    def __repr__(self):
        return f"Transaction('{self.amount}', '{self.description}', '{self.transaction_type}', '{self.date}')"
