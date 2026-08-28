import os
from datetime import datetime
from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv

load_dotenv()

db = SQLAlchemy()
migrate = Migrate()
limiter = Limiter(key_func=get_remote_address, default_limits=['200 per day', '50 per hour'])


def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///betting_app.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'dev-jwt-secret-key')
    app.config['CORS_HEADERS'] = 'Content-Type'

    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app, resources={r'/api/*': {'origins': os.getenv('CORS_ORIGINS', 'http://localhost:5173').split(',')}}, supports_credentials=True)
    limiter.init_app(app)

    from app.routes.auth import auth_bp
    from app.routes.games import games_bp
    from app.routes.wallet import wallet_bp
    from app.routes.bids import bids_bp
    from app.routes.admin import admin_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(games_bp, url_prefix='/api')
    app.register_blueprint(wallet_bp, url_prefix='/api')
    app.register_blueprint(bids_bp, url_prefix='/api')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')

    from app.models import User, Game, Bid, Transaction, DepositRequest, WithdrawalRequest, GameResult, Notification, Setting, AdminAuditLog
    with app.app_context():
        db.create_all()
        seed_default_data(app)

    return app


def seed_default_data(app):
    from app.models import Game, User, Setting
    from app import db
    from werkzeug.security import generate_password_hash
    import os

    if User.query.filter_by(username='admin').first() is None:
        admin_user = User(
            name='Administrator',
            username=os.getenv('ADMIN_USERNAME', 'admin'),
            mobile='9999999999',
            email=os.getenv('ADMIN_EMAIL', 'admin@example.com'),
            password_hash=generate_password_hash(os.getenv('ADMIN_PASSWORD', 'admin123')),
            role='admin',
            status='approved',
            wallet_balance=0,
        )
        db.session.add(admin_user)

    games = [
        'Main Bazar', 'Rajdhani Night', 'Kalyan Night', 'Milan Night', 'Rajyog Night',
        'Madhur Night', 'Padmavati Night', 'Shridevi Night', 'Kalyan', 'Milan Day',
        'Rajdhani Day', 'Rajyog Day', 'Madhur Day', 'Time Bazar'
    ]
    for idx, name in enumerate(games, start=1):
        if Game.query.filter_by(name=name).first() is None:
            game = Game(name=name, slug=name.lower().replace(' ', '-'), is_running=(idx <= 3), open_time='09:00', close_time='23:59', sort_order=idx)
            db.session.add(game)

    if Setting.query.filter_by(key='rates').first() is None:
        db.session.add(Setting(key='rates', value={
            'single_digit': 9,
            'jodi_digit': 90,
            'single_panna': 140,
            'double_panna': 280,
            'triple_panna': 900,
            'half_sangam': 1200,
            'full_sangam': 10000,
        }))

    db.session.commit()
