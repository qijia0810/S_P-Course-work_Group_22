from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import event
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

db = SQLAlchemy()


class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(30), unique=True, nullable=False)
    password_hash = db.Column(db.String(1024), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    auctions = db.relationship('Auction', backref='owner', lazy=True)
    bids = db.relationship('Bid', backref='bidder', lazy=True)
    sessions = db.relationship('Session', backref='user', lazy=True)

    def set_password(self, password):
        # self.password_hash = password
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        # check=(self.password_hash == password)
        # return check
        return check_password_hash(self.password_hash, password)


class Auction(db.Model):
    __tablename__ = 'auctions'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    start_price = db.Column(db.Float, nullable=False)  # 改为 Float
    current_price = db.Column(db.Float, nullable=False, default=0.00)  # 默认值 float
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.String(10), default='active')  # 'active' or 'closed'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    end_time = db.Column(db.DateTime, nullable=False)

    bids = db.relationship('Bid', backref='auction', lazy=True)


    @property
    def is_active(self):
        """Automatically determines status based on time"""
        if self.status == 'closed':
            return False
        return self.end_time > datetime.utcnow()  # 需要添加 end_time 字段


    @property
    def highest_bid(self):
        highest = Bid.query.filter_by(auction_id=self.id).order_by(Bid.bid_amount.desc()).first()
        return highest.bid_amount if highest else self.start_price


    def update_auction_status(mapper, connection, target):
        """Automatic update of auction status"""
        if hasattr(target, 'end_time') and target.end_time:
            if target.end_time <= datetime.utcnow():
                target.status = 'closed'
            else:
                target.status = 'active'

class Bid(db.Model):
    __tablename__ = 'bids'

    id = db.Column(db.Integer, primary_key=True)
    auction_id = db.Column(db.Integer, db.ForeignKey('auctions.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    bid_amount = db.Column(db.Float, nullable=False, default=0.00)  # 改为 Float
    bid_time = db.Column(db.DateTime, default=datetime.utcnow)


class Session(db.Model):
    __tablename__ = 'sessions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    token = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)