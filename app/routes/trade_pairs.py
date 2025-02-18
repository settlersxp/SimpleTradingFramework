from flask import Blueprint, jsonify, request, render_template
from app.models.trade_pairs import TradePairs
from app import db

bp = Blueprint('trade_pairs', __name__, url_prefix='/trade_pairs')


@bp.route('/', methods=['GET'])
def index():
    trade_pairs = TradePairs.query.all()
    return render_template('trade_pairs/index.html', trade_pairs=trade_pairs)


@bp.route('/pairs', methods=['GET', 'POST', 'PUT', 'DELETE'])
def handle_pairs():
    if request.method == 'GET':
        trade_pairs = TradePairs.query.all()
        return jsonify([pair.to_dict() for pair in trade_pairs])
    elif request.method == 'POST':
        data = request.get_json()
        trade_pair = TradePairs(name=data['name'])
        db.session.add(trade_pair)
        db.session.commit()
        return jsonify(trade_pair.to_dict()), 201
    elif request.method == 'PUT':
        data = request.get_json()
        trade_pair = TradePairs.query.get_or_404(data['id'])
        trade_pair.name = data['name']
        db.session.commit()
        return jsonify(trade_pair.to_dict())
    elif request.method == 'DELETE':
        data = request.get_json()
        trade_pair = TradePairs.query.get_or_404(data['id'])
        db.session.delete(trade_pair)
        db.session.commit()
        return '', 204
