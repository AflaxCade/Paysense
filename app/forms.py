from flask_wtf import FlaskForm
from flask_login import current_user
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField,DecimalField,SelectField,\
    TextAreaField,DateField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError,InputRequired,Optional
from app.models import User
from datetime import date

# This class represents a form used for creating or updating an account.
class AccountForm(FlaskForm):
    account_name = StringField('Account name',validators=[DataRequired(), Length(min=3, max=100)])
    #balance = DecimalField('Balance', validators=[DataRequired()])
    balance = DecimalField('Balance', validators=[InputRequired()])
    submit = SubmitField('Create')

    def validate_balance(self, balance):
        if balance.data < 0:
            raise ValidationError('Balance cannot be a negative number or below a zero.')


# This class represents a form used depositing money
class DepositForm(FlaskForm):
    account_number = SelectField('Account Name', validators=[InputRequired()], choices=[])
    amount = DecimalField('Amount', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    date = DateField('Select Date', validators=[DataRequired()], default=date.today)
    submit = SubmitField('Deposit')

    def validate_amount(self, amount):
        if amount.data < 0:
            raise ValidationError('Amount cannot be a negative number or below a zero.')
        

# This class represents a form used for deposit
class UpdateDepositForm(FlaskForm):
    account_number = StringField('Account Name', validators=[DataRequired()])
    amount = DecimalField('Amount', validators=[DataRequired()])
    description = StringField('Description', validators=[DataRequired()])
    date = DateField('Select Date', validators=[DataRequired()], default=date.today)
    submit = SubmitField('Update')

    def validate_amount(self, amount):
        if amount.data < 0:
            raise ValidationError('Amount cannot be a negative number or below a zero.')


# This class represents a form used Withdrawing money
class WithdrawalForm(FlaskForm):
    account_number = SelectField('Account Name', validators=[InputRequired()], choices=[])
    amount = DecimalField('Amount', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    date = DateField('Select Date', validators=[DataRequired()], default=date.today)
    submit = SubmitField('Withdraw')

    def validate_amount(self, amount):
        if amount.data < 0:
            raise ValidationError('Amount cannot be a negative number or below a zero.')


# This class represents a form used for Withdrawal
class UpdateWithdrawalForm(FlaskForm):
    account_number = StringField('Account Name', validators=[DataRequired()])
    amount = DecimalField('Amount', validators=[DataRequired()])
    description = StringField('Description', validators=[DataRequired()])
    date = DateField('Select Date', validators=[DataRequired()], default=date.today)
    submit = SubmitField('Update')

    def validate_amount(self, amount):
        if amount.data < 0:
            raise ValidationError('Amount cannot be a negative number or below a zero.')


# This class represents a form used for creating a user.
class RegistrationForm(FlaskForm):
    username = StringField('Username',validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',validators=[DataRequired(), EqualTo('password')])
    user_type = SelectField('UserType', validators=[InputRequired()], choices=[('','Select User Type'),('Admin','Admin'),('User','User')])
    submit = SubmitField('Create')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')


# This class represents a form used for updating a user.
class UpdateUserForm(FlaskForm):
    username = StringField('Username',validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',validators=[DataRequired(), Email()])
    user_type = SelectField('UserType', validators=[InputRequired()], choices=[('','Select User Type'),('Admin','Admin'),('User','User')])
    submit = SubmitField('Update')


# This class represents a form used for updating a profile.
class UpdateProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',validators=[DataRequired(), Email()])
    picture = FileField('Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is taken. Please choose a different one.')


# This class represents a form used for login
class LoginForm(FlaskForm):
    email = StringField('Email',validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


# This class represents a form used requesting reset password
class RequestResetForm(FlaskForm):
    email = StringField('Email',validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('There is no account with that email. You must register first.')


# This class represents a form used reseting password
class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')


# This class represents a form used for updating a user.
class FilterForm(FlaskForm):
    transaction_type = SelectField('Transaction Type', choices=[('','Select Transaction Type'),('','All'),('Deposit','Deposit'),('Withdraw','Withdraw')])
    submit = SubmitField('Filter')