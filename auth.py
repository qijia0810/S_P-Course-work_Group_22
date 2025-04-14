from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from models import User, db, Session
from datetime import datetime, timedelta
import secrets

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        remember = True if request.form.get('remember') else False

        # 1. Verify user presence
        print(f"Searching for user: {username}")
        user = User.query.filter_by(username=username).first()
        print(f"Found user: {user}")  # check if user is None
        print(f"input: {password}")
        print(f"user password: {user.password_hash}")
        print(f"check: {user.check_password(password)}")
        # 2. Verify Password
        if user and user.check_password(password):
            # 3. Create Session Token (if using custom session management)
            try:
                token = secrets.token_hex(32)
                expires_at = datetime.utcnow() + timedelta(days=1)

                new_session = Session(
                    user_id=user.id,
                    token=token,
                    expires_at=expires_at
                )
                db.session.add(new_session)
                db.session.commit()

                # 4. Execute Flask-Login login
                login_user(user, remember=remember)

                # 5. redirects
                next_page = request.args.get('next')
                return redirect(next_page or url_for('bidding.list_auctions'))

            except Exception as e:
                db.session.rollback()
                flash('Login failed due to system error', 'error')
                return redirect(url_for('auth.login'))

        # All validation failures
        flash('Invalid username or password', 'error')
        return redirect(url_for('auth.login'))

    return render_template('login.html')

@auth_bp.route('/register/', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form.get('confirm_password')

        # Simple Validation Example
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return redirect(url_for('auth.register'))

        # Verify that the username and email address already exist
        if User.query.filter_by(username=username).first():
            db.session.rollback()
            flash('Username already exists', 'error')
            return redirect(url_for('auth.register'))

        if User.query.filter_by(email=email).first():
            db.session.rollback()
            flash('Email already exists', 'error')
            return redirect(url_for('auth.register'))

        # Create New User
        new_user = User(username=username, email=email)
        # new_user.set_password(password_hash=generate_password_hash(password))
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('auth.login'))
    # return redirect(url_for('auth.register'))
    return render_template('register.html')


@auth_bp.route('/logout/')
@login_required
def logout():
    # Delete the current user's session
    Session.query.filter_by(user_id=current_user.id).delete()
    db.session.commit()

    logout_user()
    flash('You have been logged out', 'success')
    return redirect(url_for('home'))

