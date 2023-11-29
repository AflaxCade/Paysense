import os
import secrets
import datetime
from PIL import Image
from sqlalchemy import func
from flask_mail import Message
from sqlalchemy.exc import IntegrityError
from app.models import Account,User,Transaction
from app import app, db, bcrypt,mail
from decimal import Decimal, ROUND_DOWN
from flask import render_template,redirect,url_for,request,flash,abort
from flask_login import login_user, current_user, logout_user, login_required
from app.forms import AccountForm,RegistrationForm,UpdateUserForm,LoginForm,UpdateProfileForm,FilterForm,\
    RequestResetForm,ResetPasswordForm,DepositForm,WithdrawalForm,UpdateDepositForm,UpdateWithdrawalForm


# Route that handles the homepage and displays a dashboard with summary information
@app.route("/", strict_slashes=False)
@login_required
def home():
    # Get the current user's account numbers
    user_account_numbers = [account.account_number for account in current_user.accounts]
    account_count = Account.query.count() if current_user.usertype == 'Admin' else Account.query.filter_by(owner=current_user).count()
    users = User.query.count()
    balance = db.session.query(func.sum(Account.balance)).scalar() if current_user.usertype == 'Admin' else db.session.query(func.sum(Account.balance)).filter_by(owner=current_user).scalar()
    if current_user.usertype == 'Admin':
        deposits = db.session.query(func.sum(Transaction.amount)).filter(Transaction.transaction_type == 'Deposit').scalar()
    else:
        deposits = db.session.query(func.sum(Transaction.amount)) \
            .filter(Transaction.account_number.in_(user_account_numbers),
                Transaction.transaction_type == 'Deposit') \
            .scalar()
    if current_user.usertype == 'Admin':
        withdraws = db.session.query(func.sum(Transaction.amount)).filter(Transaction.transaction_type == 'Withdraw').scalar()
    else:
        withdraws = db.session.query(func.sum(Transaction.amount)) \
            .filter(Transaction.account_number.in_(user_account_numbers),
                Transaction.transaction_type == 'Withdraw') \
            .scalar()
    transaction = Transaction.query.count() if current_user.usertype == 'Admin' else Transaction.query.filter(Transaction.account_number.in_(user_account_numbers)).count()
    current_year = datetime.datetime.now().year
    today = datetime.datetime.now().date().strftime("%Y-%m-%d")
    if current_user.usertype == 'Admin':
        trans_count = Transaction.query.filter(Transaction.date.like(f"{today}%")).count()
    else:
        trans_count = Transaction.query.filter(
        Transaction.account_number.in_(user_account_numbers),
        Transaction.date.like(f"{today}%")
        ).count()
    admins = User.query.filter(User.usertype == "Admin").count()
    return render_template('dashboard.html', title='Home',totalAccounts=account_count,totalBalance=balance,totalUser=users,admins=admins,\
        totalTransaction=transaction,totalDeposit=deposits,totalwithdraw=withdraws,trans_count=trans_count,current_year=current_year)


# Route that handles the accounts page and displays a list of accounts
@app.route("/accounts", strict_slashes=False)
@login_required
def accounts():
    form = AccountForm()
    current_year = datetime.datetime.now().year
    if current_user.usertype == "Admin":
        accounts = Account.query.order_by(Account.account_number.asc())
    else:
        accounts = Account.query.filter_by(owner=current_user).order_by(Account.account_number.asc())
    return render_template('accounts.html', title='Accounts',form=form,accounts=accounts,current_year=current_year)


# Route that handles the creation of a new account
@app.route('/createAccount',methods=['GET','POST'])
@login_required
def add_account():
    form = AccountForm()
    if form.validate_on_submit():
        balance = Decimal(form.balance.data).quantize(Decimal('0.00'), rounding=ROUND_DOWN)
        acc = Account(account_name=form.account_name.data, balance=str(balance),owner=current_user)
        db.session.add(acc)
        db.session.commit()
        flash("Account created successfully", "success")
        return redirect(url_for('accounts'))
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"{field}: {error}", "danger")
    return redirect(url_for('accounts'))


# Route that handles updating an individual account
@app.route('/accounts/<int:account_number>/update', methods=['POST'])
@login_required
def update_account(account_number):
    account = Account.query.get_or_404(account_number)
    if account.owner != current_user:
        abort(403)
    form = AccountForm()
    if form.validate_on_submit():
        balance = Decimal(form.balance.data).quantize(Decimal('0.00'), rounding=ROUND_DOWN)
        account.account_name = form.account_name.data
        account.balance = str(balance)
        db.session.commit()
        flash("Account Updated successfully", "success")
        return redirect(url_for('accounts'))
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"{field}: {error}", "danger")
    return redirect(url_for('accounts'))


@app.route('/accounts/<int:account_number>/delete', methods=['POST'])
@login_required
def delete_account(account_number):
    try:
        account = Account.query.filter_by(account_number=account_number).first()
        if account.owner != current_user:
            abort(403)
        if account:
            db.session.delete(account)
            db.session.commit()
            flash("Account deleted successfully", "success")
        else:
            flash("Account not found", "danger")
        return redirect(url_for('accounts'))
    except IntegrityError:
        db.session.rollback()
        flash("Failed to delete account. Please check for any associated data.", "danger")
        return redirect(url_for('accounts'))


# Route that handles adding the deposits and displays a list of deposits
@app.route("/deposits", methods=['GET', 'POST'], strict_slashes=False)
@login_required
def deposits():
    form = DepositForm()
    updateForm = UpdateDepositForm()
    accounts = Account.query.all() if current_user.usertype == 'Admin' else Account.query.filter_by(owner=current_user).all()
    account_choices = [('','Select The Account')] + [(acc.account_number,acc.account_name) for acc in accounts]
    form.account_number.choices = account_choices
    if form.validate_on_submit():
        amount = Decimal(form.amount.data).quantize(Decimal('0.00'), rounding=ROUND_DOWN)
        account_number = form.account_number.data
        deposit = Transaction(account_number=account_number, amount=str(amount), description=form.description.data, transaction_type='Deposit',date=form.date.data)
        db.session.add(deposit)
        db.session.commit()
        # Update the account balance
        account = Account.query.get(account_number)
        account.balance += amount
        db.session.commit()
        flash("The Account has been deposited successfully", "success")
        return redirect(url_for('deposits'))
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"{field}: {error}", "danger")
    current_year = datetime.datetime.now().year
    # Get the current user's account numbers
    user_account_numbers = [account.account_number for account in current_user.accounts]
    # Filter transactions by account numbers and transaction type
    if current_user.usertype == 'Admin':
        deposits = Transaction.query.filter_by(transaction_type='Deposit').order_by(Transaction.transaction_id.asc())
    else:
        deposits = Transaction.query.filter(Transaction.account_number.in_(user_account_numbers),Transaction.transaction_type == 'Deposit').order_by(Transaction.transaction_id.asc()).all()
    return render_template('deposits.html', title='Deposits', form=form, updateForm=updateForm, deposits=deposits,current_year=current_year)


# Route that handles updating the deposits
@app.route('/deposits/<int:id>/update', methods=['GET', 'POST'])
@login_required
def update_deposit(id):
    deposit = Transaction.query.get_or_404(id)
    form = UpdateDepositForm()
    if form.validate_on_submit():
        amount_diff = Decimal(form.amount.data).quantize(Decimal('0.00'), rounding=ROUND_DOWN) - deposit.amount
        deposit.amount = Decimal(form.amount.data).quantize(Decimal('0.00'), rounding=ROUND_DOWN)
        deposit.description = form.description.data
        deposit.date = form.date.data
        # Update the account balance
        account = Account.query.get(deposit.account_number)
        account.balance += amount_diff
        db.session.commit()
        flash("The transaction and account balance have been updated successfully.", "success")
        return redirect(url_for('deposits'))
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"{field}: {error}", "danger")
    return redirect(url_for('deposits'))


# Route that handles the deletion of a deposit
@app.route('/deposits/<int:id>/delete', methods=['POST'])
@login_required
def delete_deposit(id):
    deposit = Transaction.query.get_or_404(id)
    amount = Decimal(deposit.amount).quantize(Decimal('0.00'), rounding=ROUND_DOWN)
    account_number = deposit.account_number
    # Update the account balance if sufficient balance is available
    account = Account.query.get(account_number)
    if account.balance >= amount:
        account.balance -= amount
        db.session.commit()
        db.session.delete(deposit)
        db.session.commit()
        flash("The transaction has been deleted successfully.", "success")
    else:
        flash("Insufficient balance to delete the transaction.", "danger")
    return redirect(url_for('deposits'))


@app.route("/withdrawals", methods=['GET', 'POST'], strict_slashes=False)
@login_required
def withdrawals():
    form = WithdrawalForm()
    updateForm = UpdateWithdrawalForm()
    accounts = Account.query.all() if current_user.usertype == 'Admin' else Account.query.filter_by(owner=current_user).all()
    account_choices = [('','Select The Account')] + [(acc.account_number,acc.account_name) for acc in accounts]
    form.account_number.choices = account_choices
    if form.validate_on_submit():
        amount = Decimal(form.amount.data).quantize(Decimal('0.00'), rounding=ROUND_DOWN)
        account_number = form.account_number.data
        account = Account.query.get(account_number)
        if account.balance >= amount:
            withdraw = Transaction(account_number=account_number, amount=str(amount), description=form.description.data, transaction_type='Withdraw',date=form.date.data)
            db.session.add(withdraw)
            db.session.commit()
            account.balance -= amount
            db.session.commit()
            flash("The Account has been Withdrawed successfully", "success")
        else:
            flash("Insufficient balance for withdrawal", "danger")
        return redirect(url_for('withdrawals'))
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"{field}: {error}", "danger")
    current_year = datetime.datetime.now().year
    user_account_numbers = [account.account_number for account in current_user.accounts]
    # Filter transactions by account numbers and transaction type
    if current_user.usertype == 'Admin':
        withdrawals = Transaction.query.filter_by(transaction_type='Withdraw').order_by(Transaction.transaction_id.asc())
    else:
        withdrawals = Transaction.query.filter(Transaction.account_number.in_(user_account_numbers),Transaction.transaction_type == 'Withdraw').order_by(Transaction.transaction_id.asc()).all()
    return render_template('withdrawals.html', title='Withdrawals', form=form, updateForm=updateForm, withdrawals=withdrawals,current_year=current_year)


# Route that handles updating the withdrawals
@app.route('/withdrawals/<int:id>/update', methods=['GET', 'POST'])
@login_required
def update_withdrawal(id):
    withdrawal = Transaction.query.get_or_404(id)
    form = UpdateWithdrawalForm()
    if form.validate_on_submit():
        amount_diff = Decimal(form.amount.data).quantize(Decimal('0.00'), rounding=ROUND_DOWN) - withdrawal.amount
        withdrawal.amount = Decimal(form.amount.data).quantize(Decimal('0.00'), rounding=ROUND_DOWN)
        withdrawal.description = form.description.data
        withdrawal.date = form.date.data
        # Update the account balance
        account = Account.query.get(withdrawal.account_number)
        account.balance -= amount_diff
        db.session.commit()
        flash("The transaction and account balance have been updated successfully.", "success")
        return redirect(url_for('withdrawals'))
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"{field}: {error}", "danger")
    return redirect(url_for('withdrawals'))


# Route that handles the deletion of a withdraw
@app.route('/withdrawals/<int:id>/delete', methods=['POST'])
@login_required
def delete_withdrawal(id):
    withdraw = Transaction.query.get_or_404(id)
    amount = Decimal(withdraw.amount).quantize(Decimal('0.00'), rounding=ROUND_DOWN)
    account_number = withdraw.account_number
    # Update the account balance if sufficient balance is available
    account = Account.query.get(account_number)
    account.balance += amount
    db.session.commit()
    db.session.delete(withdraw)
    db.session.commit()
    flash("The transaction has been deleted successfully.", "success")
    return redirect(url_for('withdrawals'))

# Route that handles displaying th list of all transactions
@app.route("/transactions", methods=['GET', 'POST'], strict_slashes=False)
@login_required
def transactions():
    # Get the current user's account numbers
    user_account_numbers = [account.account_number for account in current_user.accounts]
    current_year = datetime.datetime.now().year
    form = FilterForm()

    if form.validate_on_submit():
        transaction_type = form.transaction_type.data
        if transaction_type:
            if current_user.usertype == 'Admin':
                transactions = Transaction.query.filter(Transaction.transaction_type == transaction_type).order_by(Transaction.transaction_id.asc()).all()
            else:
                transactions = Transaction.query.filter(
                    Transaction.account_number.in_(user_account_numbers),
                    Transaction.transaction_type == transaction_type
                ).order_by(Transaction.transaction_id.asc()).all()
        else:
            if current_user.usertype == 'Admin':
                transactions = Transaction.query.order_by(Transaction.transaction_id.asc())
            else:
                transactions = Transaction.query.filter(
                    Transaction.account_number.in_(user_account_numbers)
                ).order_by(Transaction.transaction_id.asc()).all()
    else:
        if current_user.usertype == 'Admin':
            transactions = Transaction.query.order_by(Transaction.transaction_id.asc())
        else:
            transactions = Transaction.query.filter(
                Transaction.account_number.in_(user_account_numbers)
            ).order_by(Transaction.transaction_id.asc()).all()

    return render_template('transactions.html', title='All Transaction', transactions=transactions, current_year=current_year, form=form)


# Route that handles the users page and displays a list of users
@app.route("/users", strict_slashes=False)
@login_required
def users():
    if current_user.usertype != "Admin":
        abort(403)  # Return a Forbidden error if the username is not "Admin"
    form = RegistrationForm()
    updateform = UpdateUserForm()
    current_year = datetime.datetime.now().year
    users = User.query.order_by(User.id.asc())
    return render_template('users.html', title='Users',form=form,updateform=updateform,users=users,current_year=current_year)


# Route that handles the creation of a new user
@app.route('/createUser', methods=['GET', 'POST'])
@login_required
def add_user():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password, usertype=form.user_type.data)
        db.session.add(user)
        db.session.commit()
        flash("User created successfully", "success")
        return redirect(url_for('users'))
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"{field}: {error}", "danger")
    return redirect(url_for('users'))
    

# Route that handles updating an individual user
@app.route('/users/<int:id>/update', methods=['POST'])
@login_required
def update_user(id):
    user = User.query.get_or_404(id)
    form = UpdateUserForm()
    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        user.usertype = form.user_type.data
        db.session.commit()
        flash("User Updated successfully", "success")
        return redirect(url_for('users'))
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"{field}: {error}", "danger")
    return redirect(url_for('users'))


# Route that handles the deletion of a user
@app.route('/users/<int:id>/delete', methods=['POST'])
@login_required
def delete_user(id):
    user = User.query.filter_by(id=id).first()
    if user:
        db.session.delete(user)
        db.session.commit()
        flash("User deleted successfully", "success")
        return redirect(url_for('users'))
    else:
        return {'error': 'Account not found'}, 404
    

# Function that handles the saving picture
def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/img', picture_fn)
    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    return picture_fn


# Route that handles the user profile
@app.route("/profile", methods=['GET', 'POST'])
@login_required
def profile():
    form = UpdateProfileForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.profile_pic = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your prifile has been updated!', 'success')
        return redirect(url_for('profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='img/' + current_user.profile_pic)
    current_year = datetime.datetime.now().year
    return render_template('profile.html', title='Profile',form=form,image_file=image_file,current_year=current_year)


# Route that handles the login functionality
@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash("Login Unsuccessful. Please check email or password", "danger")
    return render_template('login.html', form=form)
    

# Route that handles the user logout functionality
@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('login'))


# Function that handles to send the user an email
def send_reset_email(user):
    token = user.get_reset_token()
    reset_url = url_for('reset_token', token=token, _external=True)
    html = f'''
        <div style="background-color: #F8F8F8; padding: 20px;">
            <div style="background-color: white; padding: 20px; border-radius: 5px;">
                <p style="font-size: 18px; margin-bottom: 10px;">Trouble logging in?</p>
                <p style="font-size: 16px; margin-bottom: 10px;">Resetting your password is easy.</p>
                <p style="font-size: 16px; margin-bottom: 10px;">Just press the button below and follow the instructions. We’ll have you up and running in no time.</p>
                <p style="text-align: center; margin-bottom: 20px;">
                    <a href="{reset_url}" style="background-color: #4CAF50; color: white; padding: 10px 40px; border-radius: 5px; border: none; text-decoration: none; display: inline-block; font-size: 14px;">Change Now</a>
                </p>
                <p style="font-size: 14px;">If you did not make this request, you can ignore this email and no changes will be made.</p>
            </div>
        </div>
    '''
    msg = Message('Password Reset Request', sender='system.idcard@gmail.com', recipients=[user.email])
    msg.html = html
    mail.send(msg)


# Route that handles requesting reset password email
@app.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('login'))
    return render_template('reset_request.html', title='Reset Password', form=form)


# Route that handles reseting the password
@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('reset_token.html', title='Reset Password', form=form)


#Forbidden access
@app.errorhandler(403)
@login_required
def page_not_found(e):
    current_year = datetime.datetime.now().year
    return render_template('403.html',current_year=current_year), 403

#Invalid URL error
@app.errorhandler(404)
@login_required
def page_not_found(e):
    current_year = datetime.datetime.now().year
    return render_template('404.html',current_year=current_year), 404


#internal server error
@app.errorhandler(500)
@login_required
def page_not_found(e):
    current_year = datetime.datetime.now().year
    return render_template('500.html',current_year=current_year), 500