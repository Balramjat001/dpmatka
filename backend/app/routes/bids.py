from flask import Blueprint, request, g
from app.models import Bid, User, Game, GameResult, Transaction
from app import db
from app.auth import require_auth, require_admin
from app.utils.validators import validate_bid_value

bids_bp = Blueprint('bids', __name__)


@bids_bp.route('/bids', methods=['POST'])
@require_auth
def place_bid():
    data = request.get_json(silent=True) or {}
    game = Game.query.get(data.get('game_id'))
    if not game:
        return {'error': 'Game not found'}, 404
    if not game.is_running:
        return {'error': 'Game is closed'}, 400
    bid_type = data.get('bid_type')
    bid_value = data.get('bid_value')
    amount = float(data.get('amount') or 0)
    if amount < 10:
        return {'error': 'Minimum bid is ₹10'}, 400
    if validate_bid_value(bid_type, bid_value) is False:
        return {'error': 'Invalid bid value'}, 400
    if g.current_user.wallet_balance < amount:
        return {'error': 'Insufficient wallet balance'}, 400
    g.current_user.wallet_balance -= amount
    bid = Bid(
        user_id=g.current_user.id,
        game_id=game.id,
        bid_type=bid_type,
        bid_value=str(bid_value),
        open_digit=data.get('open_digit'),
        close_digit=data.get('close_digit'),
        points=data.get('points', amount),
        amount=amount,
        status='placed',
        result_status='pending',
        win_amount=0,
    )
    db.session.add(bid)
    tx = Transaction(user_id=g.current_user.id, type='bet', amount=amount, balance_before=g.current_user.wallet_balance + amount, balance_after=g.current_user.wallet_balance, reference=f'bid-{bid.id or 0}', reason='Bid placed')
    db.session.add(tx)
    db.session.flush()
    bid.reference = f'bid-{bid.id}'
    db.session.commit()
    return {'message': 'Your bid is placed successfully.', 'bid': serialize_bid(bid)}, 201


@bids_bp.route('/bids/history', methods=['GET'])
@require_auth
def bid_history():
    bids = Bid.query.filter_by(user_id=g.current_user.id).order_by(Bid.created_at.desc()).all()
    return {'bids': [serialize_bid(b) for b in bids]}, 200


@bids_bp.route('/wins', methods=['GET'])
@require_auth
def win_history():
    bids = Bid.query.filter_by(user_id=g.current_user.id).filter(Bid.result_status == 'won').order_by(Bid.created_at.desc()).all()
    return {'wins': [serialize_bid(b) for b in bids]}, 200


@bids_bp.route('/admin/bets', methods=['GET'])
@require_auth
@require_admin
def admin_bets():
    bids = Bid.query.order_by(Bid.created_at.desc()).all()
    return {'bets': [serialize_bid(b) for b in bids]}, 200


@bids_bp.route('/admin/results', methods=['GET'])
@require_auth
@require_admin
def admin_results():
    games = Game.query.order_by(Game.sort_order.asc()).all()
    result_map = {}
    for game in games:
        last = GameResult.query.filter_by(game_id=game.id).order_by(GameResult.result_date.desc()).first()
        result_map[game.id] = last
    return {'results': [{
        'game_id': game.id,
        'game_name': game.name,
        'result': serialize_game_result(result_map.get(game.id))
    } for game in games]}, 200


@bids_bp.route('/admin/results', methods=['POST'])
@require_auth
@require_admin
def create_result():
    data = request.get_json(silent=True) or {}
    game_id = data.get('game_id')
    game = Game.query.get(game_id)
    if not game:
        return {'error': 'Game not found'}, 404
    result = GameResult(game_id=game.id, result_date=data.get('result_date') or __import__('datetime').datetime.utcnow(), single_digit=data.get('single_digit'), jodi_digit=data.get('jodi_digit'), single_panna=data.get('single_panna'), double_panna=data.get('double_panna'), triple_panna=data.get('triple_panna'), half_sangam=data.get('half_sangam'), full_sangam=data.get('full_sangam'))
    db.session.add(result)
    db.session.commit()
    settle_winnings(game.id, result)
    return {'message': 'Result published successfully', 'result': serialize_game_result(result)}, 201


@bids_bp.route('/admin/results/<int:result_id>', methods=['PUT'])
@require_auth
@require_admin
def update_result(result_id):
    result = GameResult.query.get_or_404(result_id)
    data = request.get_json(silent=True) or {}
    for key in ['single_digit','jodi_digit','single_panna','double_panna','triple_panna','half_sangam','full_sangam']:
        if key in data:
            setattr(result, key, data[key])
    db.session.commit()
    settle_winnings(result.game_id, result)
    return {'message': 'Result updated', 'result': serialize_game_result(result)}, 200


def settle_winnings(game_id, result):
    bids = Bid.query.filter_by(game_id=game_id).filter(Bid.result_status != 'won').all()
    for bid in bids:
        if bid.amount <= 0:
            continue
        match = False
        if bid.bid_type == 'single_digit':
            match = str(bid.bid_value) == str(result.single_digit)
        elif bid.bid_type == 'jodi_digit':
            match = str(bid.bid_value) == str(result.jodi_digit)
        elif bid.bid_type == 'single_panna':
            match = str(bid.bid_value) == str(result.single_panna)
        elif bid.bid_type == 'double_panna':
            match = str(bid.bid_value) == str(result.double_panna)
        elif bid.bid_type == 'triple_panna':
            match = str(bid.bid_value) == str(result.triple_panna)
        elif bid.bid_type == 'half_sangam':
            match = str(bid.bid_value) == str(result.half_sangam)
        elif bid.bid_type == 'full_sangam':
            match = str(bid.bid_value) == str(result.full_sangam)
        if match:
            bid.result_status = 'won'
            payout = bid.amount * 9
            if bid.bid_type == 'jodi_digit':
                payout = bid.amount * 90
            elif bid.bid_type == 'single_panna':
                payout = bid.amount * 140
            elif bid.bid_type == 'double_panna':
                payout = bid.amount * 280
            elif bid.bid_type == 'triple_panna':
                payout = bid.amount * 900
            elif bid.bid_type == 'half_sangam':
                payout = bid.amount * 1200
            elif bid.bid_type == 'full_sangam':
                payout = bid.amount * 10000
            bid.win_amount = payout
            user = bid.user
            before = user.wallet_balance or 0
            user.wallet_balance = before + payout
            db.session.add(Transaction(user_id=user.id, type='winning', amount=payout, balance_before=before, balance_after=user.wallet_balance, reference=f'win-{bid.id}', reason='Winning settlement'))
        else:
            bid.result_status = 'lost'
    db.session.commit()


def serialize_bid(bid):
    return {
        'id': bid.id,
        'user': bid.user.username if bid.user else None,
        'game': bid.game.name if bid.game else None,
        'bid_type': bid.bid_type,
        'bid_value': bid.bid_value,
        'open_digit': bid.open_digit,
        'close_digit': bid.close_digit,
        'points': bid.points,
        'amount': bid.amount,
        'status': bid.status,
        'result_status': bid.result_status,
        'win_amount': bid.win_amount,
        'created_at': bid.created_at.isoformat() if bid.created_at else None,
    }


def serialize_game_result(result):
    if not result:
        return None
    return {
        'id': result.id,
        'single_digit': result.single_digit,
        'jodi_digit': result.jodi_digit,
        'single_panna': result.single_panna,
        'double_panna': result.double_panna,
        'triple_panna': result.triple_panna,
        'half_sangam': result.half_sangam,
        'full_sangam': result.full_sangam,
    }
