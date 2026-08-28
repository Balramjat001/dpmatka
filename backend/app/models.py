from app import db
from datetime import datetime
from sqlalchemy import JSON


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    mobile = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), nullable=True)
    password_hash = db.Column(db.String(255), nullable=False)
    wallet_balance = db.Column(db.Float, default=0.0)
    role = db.Column(db.String(20), default='user')
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Game(db.Model):
    __tablename__ = 'games'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    slug = db.Column(db.String(120), unique=True, nullable=False)
    is_running = db.Column(db.Boolean, default=False)
    open_time = db.Column(db.String(20), default='09:00')
    close_time = db.Column(db.String(20), default='23:59')
    display_result = db.Column(db.String(120), nullable=True)
    sort_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Bid(db.Model):
    __tablename__ = 'bids'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    game_id = db.Column(db.Integer, db.ForeignKey('games.id'), nullable=False)
    bid_type = db.Column(db.String(50), nullable=False)
    bid_value = db.Column(db.String(50), nullable=False)
    open_digit = db.Column(db.String(20), nullable=True)
    close_digit = db.Column(db.String(20), nullable=True)
    points = db.Column(db.Float, default=0)
    amount = db.Column(db.Float, default=0)
    status = db.Column(db.String(20), default='pending')
    result_status = db.Column(db.String(20), default='pending')
    win_amount = db.Column(db.Float, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user = db.relationship('User', backref='bids')
    game = db.relationship('Game', backref='bids')


class GameResult(db.Model):
    __tablename__ = 'game_results'
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('games.id'), nullable=False)
    result_date = db.Column(db.DateTime, default=datetime.utcnow)
    single_digit = db.Column(db.String(20), nullable=True)
    jodi_digit = db.Column(db.String(20), nullable=True)
    single_panna = db.Column(db.String(20), nullable=True)
    double_panna = db.Column(db.String(20), nullable=True)
    triple_panna = db.Column(db.String(20), nullable=True)
    half_sangam = db.Column(db.String(20), nullable=True)
    full_sangam = db.Column(db.String(20), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Transaction(db.Model):
    __tablename__ = 'transactions'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    type = db.Column(db.String(30), nullable=False)
    amount = db.Column(db.Float, default=0.0)
    balance_before = db.Column(db.Float, default=0.0)
    balance_after = db.Column(db.Float, default=0.0)
    reference = db.Column(db.String(120), nullable=True)
    reason = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(30), default='success')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref='transactions')


class DepositRequest(db.Model):
    __tablename__ = 'deposit_requests'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    amount = db.Column(db.Float, default=0.0)
    payment_method = db.Column(db.String(50), default='auto')
    transaction_reference = db.Column(db.String(120), nullable=True)
    status = db.Column(db.String(30), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user = db.relationship('User', backref='deposits')


class WithdrawalRequest(db.Model):
    __tablename__ = 'withdrawal_requests'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    amount = db.Column(db.Float, default=0.0)
    account_holder_name = db.Column(db.String(120), nullable=True)
    account_number = db.Column(db.String(50), nullable=True)
    confirm_account_number = db.Column(db.String(50), nullable=True)
    branch = db.Column(db.String(120), nullable=True)
    ifsc = db.Column(db.String(30), nullable=True)
    upi_id = db.Column(db.String(120), nullable=True)
    status = db.Column(db.String(30), default='pending')
    admin_note = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user = db.relationship('User', backref='withdrawals')


class Notification(db.Model):
    __tablename__ = 'notifications'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Setting(db.Model):
    __tablename__ = 'settings'
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(80), unique=True, nullable=False)
    value = db.Column(JSON, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class AdminAuditLog(db.Model):
    __tablename__ = 'admin_audit_logs'
    id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    action = db.Column(db.String(200), nullable=False)
    details = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    admin = db.relationship('User', backref='audit_logs')
