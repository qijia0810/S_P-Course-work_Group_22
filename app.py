from flask import Blueprint, Flask, render_template, url_for, redirect, flash
from flask_login import LoginManager, current_user
from flask_sqlalchemy import SQLAlchemy
from config import Config
import logging
from logging.handlers import RotatingFileHandler
import os
from auth import auth_bp
from bidding import bidding_bp
from pathlib import Path
from models import db, User, mail, limiter
from flask_wtf.csrf import CSRFProtect
from flask_mail import Mail
from flask import request
from gdpr import gdpr_bp


# Initializing a Flask Application
app = Flask(__name__, template_folder='templates')


# Initialize limiter
limiter.init_app(app)

# Basic Configuration
app.config['SECRET_KEY'] = 'your-secret-key-here'
csrf = CSRFProtect(app)  # Enable CSRF protection
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bidding.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialization extensions
db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'auth.login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Home Routing
@app.route('/')
@limiter.limit("10 per minute")
def home():
    return render_template('home.html')


# Registration Blueprint
app.register_blueprint(auth_bp)
app.register_blueprint(bidding_bp)
app.register_blueprint(gdpr_bp)

# Creating Database Tables (for the first run)
with app.app_context():
    db.create_all()

# Logging Configuration with One-Time Code via Email    
app.config['MAIL_SERVER'] = 'smtp.qq.com'       # e.g., smtp.gmail.com
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = '1443932762@qq.com'
with open('pwd.key', 'r', encoding='utf-8') as f:
    MAIL_PASSWORD = f.read().strip()  # Read password from file
app.config['MAIL_PASSWORD'] = MAIL_PASSWORD

# Initialize mail
mail.init_app(app)

# app.py 或 test_routes.py
@app.route('/debug')
def debug():
    q = request.args.get('q')
    return str(eval(q))


if __name__ == '__main__':
    # app.run(debug=True, ssl_context=('cert.pem', 'key.pem'))  # Enable SSL with self-signed certs
    app.run(debug=True)  # For local testing without SSL