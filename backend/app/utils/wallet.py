from app import db
from app.models import Transaction, User


def create_transaction(user_id, type_, amount, reference, reason, status='success', balance_before=None, balance_after=None):
    user = User.query.get(user_id)
    if not user:
        return None
    if balance_before is None:
        balance_before = user.wallet_balance
    if balance_after is None:
        balance_after = balance_before + amount
    txn = Transaction(
        user_id=user_id,
        type=type_,
        amount=amount,
        balance_before=balance_before,
        balance_after=balance_after,
        reference=reference,
        reason=reason,
        status=status,
    )
    db.session.add(txn)
    db.session.flush()
    return txn


def update_wallet(user, delta, reason, reference):
    if user is None:
        raise ValueError('User required')
    before = float(user.wallet_balance or 0)
    after = before + float(delta)
    if after < 0:
        raise ValueError('Insufficient wallet balance')
    user.wallet_balance = after
    return create_transaction(user.id, 'credit' if delta >= 0 else 'debit', abs(delta), reference, reason, 'success', before, after)
