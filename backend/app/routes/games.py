from flask import Blueprint, request, g
from app.models import Game, GameResult
from app import db
from app.auth import require_auth, require_admin
from app.utils.validators import parse_time


games_bp = Blueprint('games', __name__)


@games_bp.route('/games', methods=['GET'])
def list_games():
    games = Game.query.order_by(Game.sort_order.asc()).all()
    return {'games': [serialize_game(game, latest_result(game.id)) for game in games]}, 200


@games_bp.route('/games/<int:game_id>', methods=['GET'])
def get_game(game_id):
    game = Game.query.get_or_404(game_id)
    result = latest_result(game.id)
    return {'game': serialize_game(game, result)}, 200


def latest_result(game_id):
    return GameResult.query.filter_by(game_id=game_id).order_by(GameResult.result_date.desc()).first()


@games_bp.route('/admin/games', methods=['GET'])
@require_auth
@require_admin
def admin_list_games():
    games = Game.query.order_by(Game.sort_order.asc()).all()
    return {'games': [serialize_game(game) for game in games]}, 200


@games_bp.route('/admin/games/<int:game_id>', methods=['PUT'])
@require_auth
@require_admin
def update_game(game_id):
    game = Game.query.get_or_404(game_id)
    data = request.get_json(silent=True) or {}
    if 'name' in data:
        game.name = data['name']
    if 'is_running' in data:
        game.is_running = bool(data['is_running'])
    if 'open_time' in data:
        game.open_time = data['open_time']
    if 'close_time' in data:
        game.close_time = data['close_time']
    if 'display_result' in data:
        game.display_result = data['display_result']
    if 'sort_order' in data:
        game.sort_order = int(data['sort_order'])
    db.session.commit()
    return {'game': serialize_game(game)}, 200


def serialize_game(game, result=None):
    from datetime import datetime
    if game.open_time and game.close_time:
        label = f"Bet - {game.open_time} - {game.close_time}"
    else:
        label = 'Bet - 09:00 - 23:59'
    result_display = None
    if result:
        result_display = '-'.join(filter(None, [result.single_digit, result.jodi_digit, result.single_panna]))
    return {
        'id': game.id,
        'name': game.name,
        'slug': game.slug,
        'is_running': bool(game.is_running),
        'open_time': game.open_time,
        'close_time': game.close_time,
        'display_result': result_display or game.display_result,
        'sort_order': game.sort_order,
        'bet_label': label,
        'result': serialize_result(result) if result else None,
    }


def serialize_result(result):
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
        'result_date': result.result_date.isoformat() if result.result_date else None,
    }
