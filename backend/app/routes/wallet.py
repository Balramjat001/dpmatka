from flask import Blueprint, request, g
from app.models import DepositRequest, WithdrawalRequest, Transaction, User
from app import db
from app.auth import require_auth, require_admin
from app.utils.wallet import update_wallet

wallet_bp = Blueprint('wallet', __name__)


@wallet_bp.route('/wallet', methods=['GET'])
@require_auth
def get_wallet():
    user = g.current_user
    return {'wallet_balance': user.wallet_balance}, 200


@wallet_bp.route('/deposits', methods=['POST'])
@require_auth
def create_deposit():
    data = request.get_json(silent=True) or {}
    amount = float(data.get('amount') or 0)
    if amount < 100:
        return {'error': 'Minimum deposit is ₹100'}, 400
    dep = DepositRequest(user_id=g.current_user.id, amount=amount, payment_method=data.get('payment_method', 'auto'), transaction_reference=data.get('transaction_reference', 'manual'))
    db.session.add(dep)
    db.session.commit()
    return {'message': 'Deposit request submitted successfully', 'deposit': {'id': dep.id, 'status': dep.status, 'amount': dep.amount}}, 201


@wallet_bp.route('/deposits', methods=['GET'])
@require_auth
def list_deposits():
    items = DepositRequest.query.filter_by(user_id=g.current_user.id).order_by(DepositRequest.created_at.desc()).all()
    return {'deposits': [serialize_deposit(item) for item in items]}, 200


@wallet_bp.route('/withdrawals', methods=['POST'])
@require_auth
def create_withdrawal():
    data = request.get_json(silent=True) or {}
    amount = float(data.get('amount') or 0)
    if amount < 300:
        return {'error': 'Minimum withdrawal is ₹300'}, 400
    if amount > g.current_user.wallet_balance:
        return {'error': 'Insufficient wallet balance'}, 400
    if data.get('upi_id'):
        req = WithdrawalRequest(user_id=g.current_user.id, amount=amount, upi_id=data['upi_id'], status='pending')
    else:
        if not data.get('account_holder_name') or not data.get('account_number') or not data.get('confirm_account_number'):
            return {'error': 'Bank account details are required'}, 400
        if data.get('account_number') != data.get('confirm_account_number'):
            return {'error': 'Account numbers do not match'}, 400
        req = WithdrawalRequest(user_id=g.current_user.id, amount=amount, account_holder_name=data['account_holder_name'], account_number=data['account_number'], confirm_account_number=data['confirm_account_number'], branch=data.get('branch'), ifsc=data.get('ifsc'), status='pending')
    db.session.add(req)
    db.session.commit()
    return {'message': 'Withdrawal request submitted successfully', 'withdrawal': {'id': req.id, 'status': req.status, 'amount': req.amount}}, 201


@wallet_bp.route('/withdrawals', methods=['GET'])
@require_auth
def list_withdrawals():
    items = WithdrawalRequest.query.filter_by(user_id=g.current_user.id).order_by(WithdrawalRequest.created_at.desc()).all()
    return {'withdrawals': [serialize_withdrawal(item) for item in items]}, 200


@wallet_bp.route('/transactions', methods=['GET'])
@require_auth
def list_transactions():
    items = Transaction.query.filter_by(user_id=g.current_user.id).order_by(Transaction.created_at.desc()).all()
    return {'transactions': [serialize_transaction(item) for item in items]}, 200


@wallet_bp.route('/admin/deposits', methods=['GET'])
@require_auth
@require_admin
def admin_deposits():
    items = DepositRequest.query.order_by(DepositRequest.created_at.desc()).all()
    return {'deposits': [serialize_deposit(item) for item in items]}, 200


@wallet_bp.route('/admin/deposits/<int:deposit_id>', methods=['PATCH'])
@require_auth
@require_admin
def approve_deposit(deposit_id):
    dep = DepositRequest.query.get_or_404(deposit_id)
    if dep.status in ('approved', 'rejected'):
        return {'error': 'Deposit already processed'}, 400
    data = request.get_json(silent=True) or {}
    dep.status = 'approved' if data.get('action') != 'reject' else 'rejected'
    if dep.status == 'approved':
        user = dep.user
        before = user.wallet_balance or 0
        user.wallet_balance = before + dep.amount
        txn = Transaction(user_id=user.id, type='deposit', amount=dep.amount, balance_before=before, balance_after=user.wallet_balance, reference=f'deposit-{dep.id}', reason='Deposit approved')
        db.session.add(txn)
    db.session.commit()
    return {'message': 'Deposit updated', 'deposit': serialize_deposit(dep)}, 200


@wallet_bp.route('/admin/withdrawals', methods=['GET'])
@require_auth
@require_admin
def admin_withdrawals():
    items = WithdrawalRequest.query.order_by(WithdrawalRequest.created_at.desc()).all()
    return {'withdrawals': [serialize_withdrawal(item) for item in items]}, 200


@wallet_bp.route('/admin/withdrawals/<int:withdrawal_id>', methods=['PATCH'])
@require_auth
@require_admin
def update_withdrawal(withdrawal_id):
    item = WithdrawalRequest.query.get_or_404(withdrawal_id)
    data = request.get_json(silent=True) or {}
    action = data.get('action', 'process')
    if action == 'reject':
        item.status = 'rejected'
    elif action == 'success':
        if item.status != 'processing':
            item.status = 'processing'
        item.status = 'success'
        user = item.user
        before = user.wallet_balance or 0
        if before < item.amount:
            return {'error': 'Insufficient balance'}, 400
        user.wallet_balance = before - item.amount
        txn = Transaction(user_id=user.id, type='withdrawal', amount=item.amount, balance_before=before, balance_after=user.wallet_balance, reference=f'withdrawal-{item.id}', reason='Withdrawal successful')
        db.session.add(txn)
    else:
        item.status = 'processing'
    db.session.commit()
    return {'message': 'Withdrawal updated', 'withdrawal': serialize_withdrawal(item)}, 200


def serialize_deposit(item):
    return {'id': item.id, 'user': item.user.username if item.user else None, 'amount': item.amount, 'payment_method': item.payment_method, 'transaction_reference': item.transaction_reference, 'status': item.status, 'created_at': item.created_at.isoformat() if item.created_at else None}


def serialize_withdrawal(item):
    return {'id': item.id, 'user': item.user.username if item.user else None, 'mobile': item.user.mobile if item.user else None, 'amount': item.amount, 'bank_or_upi': item.upi_id or f"{item.account_holder_name} / {item.account_number}", 'status': item.status, 'requested_at': item.created_at.isoformat() if item.created_at else None}


def serialize_transaction(item):
    return {'id': item.id, 'type': item.type, 'amount': item.amount, 'balance_before': item.balance_before, 'balance_after': item.balance_after, 'status': item.status, 'description': item.reason, 'created_at': item.created_at.isoformat() if item.created_at else None}
