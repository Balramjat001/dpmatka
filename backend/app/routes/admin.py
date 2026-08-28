from flask import Blueprint, request, g
from app.models import User, DepositRequest, WithdrawalRequest, Bid, Game, Transaction, GameResult, Notification
from app import db
from app.auth import require_auth, require_admin
from app.routes.auth import serialize_user

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/dashboard', methods=['GET'])
@require_auth
@require_admin
def dashboard():
    total_users = User.query.count()
    total_wallet = sum(user.wallet_balance or 0 for user in User.query.all())
    pending_bets = Bid.query.filter_by(status='placed').count()
    payment_queue = DepositRequest.query.filter_by(status='pending').count()
    withdrawal_queue = WithdrawalRequest.query.filter_by(status='pending').count()
    return {
        'stats': {
            'users': total_users,
            'total_wallet': total_wallet,
            'pending_bets': pending_bets,
            'payment_queue': payment_queue,
            'withdrawal_queue': withdrawal_queue,
        }
    }, 200


@admin_bp.route('/users', methods=['GET'])
@require_auth
@require_admin
def list_users():
    users = User.query.order_by(User.created_at.desc()).all()
    return {'users': [serialize_user(user) for user in users]}, 200


@admin_bp.route('/users/<int:user_id>', methods=['PATCH'])
@require_auth
@require_admin
def update_user(user_id):
    user = User.query.get_or_404(user_id)
    data = request.get_json(silent=True) or {}
    if 'status' in data:
        user.status = data['status']
    if 'role' in data:
        user.role = data['role']
    if 'wallet_balance' in data:
        user.wallet_balance = float(data['wallet_balance'])
    db.session.commit()
    return {'user': serialize_user(user)}, 200


@admin_bp.route('/registrations', methods=['GET'])
@require_auth
@require_admin
def registrations():
    users = User.query.filter(User.status.in_(['pending', 'rejected'])).order_by(User.created_at.desc()).all()
    return {'users': [serialize_user(user) for user in users]}, 200


@admin_bp.route('/registrations/<int:user_id>', methods=['PATCH'])
@require_auth
@require_admin
def approve_registration(user_id):
    user = User.query.get_or_404(user_id)
    data = request.get_json(silent=True) or {}
    action = data.get('action', 'approve')
    user.status = 'approved' if action == 'approve' else 'rejected'
    db.session.commit()
    return {'message': 'Registration updated', 'user': serialize_user(user)}, 200


@admin_bp.route('/results', methods=['GET'])
@require_auth
@require_admin
def admin_results():
    results = []
    for game in Game.query.order_by(Game.sort_order.asc()).all():
        latest = GameResult.query.filter_by(game_id=game.id).order_by(GameResult.created_at.desc()).first()
        results.append({
            'game_id': game.id,
            'game_name': game.name,
            'result': latest,
        })
    return {'results': results}, 200


@admin_bp.route('/transactions', methods=['GET'])
@require_auth
@require_admin
def all_transactions():
    items = Transaction.query.order_by(Transaction.created_at.desc()).all()
    return {'transactions': [serialize_txn(item) for item in items]}, 200


@admin_bp.route('/notifications', methods=['GET'])
@require_auth
@require_admin
def admin_notifications():
    notes = Notification.query.order_by(Notification.created_at.desc()).all()
    return {'notifications': [serialize_note(item) for item in notes]}, 200


def serialize_txn(item):
    return {'id': item.id, 'user': item.user.username if item.user else None, 'type': item.type, 'amount': item.amount, 'status': item.status, 'description': item.reason, 'created_at': item.created_at.isoformat() if item.created_at else None}


def serialize_note(item):
    return {'id': item.id, 'title': item.title, 'message': item.message, 'is_read': item.is_read, 'created_at': item.created_at.isoformat() if item.created_at else None}
