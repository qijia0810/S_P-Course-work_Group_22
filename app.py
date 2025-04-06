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
from models import db, User
from flask_wtf.csrf import CSRFProtect

# Initializing a Flask Application
app = Flask(__name__, template_folder='templates')

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
def home():
    return render_template('home.html')


# Registration Blueprint
app.register_blueprint(auth_bp)
app.register_blueprint(bidding_bp)

# Creating Database Tables (for the first run)
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)