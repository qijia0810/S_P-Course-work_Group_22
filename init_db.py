from pathlib import Path
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from werkzeug.security import generate_password_hash
from models import User, db, Session, Auction, Bid
from datetime import datetime, timedelta
from decimal import Decimal

# Manually initializing a Flask application
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bidding.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-secret-key-here'

# Initialization extensions
db = SQLAlchemy(app)
login_manager = LoginManager(app)

# def clear_existing_data():
#     """Secure cleansing of old data"""
#     db_path = Path("instance/bidding.db")
#     if db_path.exists():
#         try:
#             with app.app_context():
#                 db.drop_all()
#                 db.create_all()
#             print("数据库已重置")
#         except Exception as e:
#             print(f"清理失败: {str(e)}")
#             os.remove(db_path)  # 强制删除文件
#             db.create_all()
#
#     # clear_existing_data()

with app.app_context():
    # Create all tables
    db.create_all()

    # Add test data
    test_user = User(
        username='test',
        email='test@example.com',
        password_hash='test'
    )
    # print(f"user: {test_user1.set_password(test_user1.password_hash)}")
    db.session.add(test_user)

    alice = User(
        username='alice',
        email='alice@example.com',
        password_hash='alice123'
    )
    db.session.add(alice)

    bob = User(
        username='bob',
        email='bob@example.com',
        password_hash='bob123'
    )
    db.session.add(bob)

    db.session.commit()

    # Add Test Auction
    macbook_auction = Auction(
        title='MacBook Pro',
        description='Latest model, brand new.',
        start_price=1000.00,
        current_price=1000.00,
        owner_id=alice.id,
        end_time = datetime.utcnow() + timedelta(days=7),  # Ends in 7 days
        created_at=datetime.utcnow()
    )
    db.session.add(macbook_auction)

    db.session.commit()

    # Add a test bid
    bob_bid = Bid(
        auction_id=macbook_auction.id,
        user_id=bob.id,
        bid_amount=1100.00
    )
    db.session.add(bob_bid)

    # Update Current Prices
    macbook_auction.current_price = 1100.00

    db.session.commit()

    print("Database initialized with test data.")

