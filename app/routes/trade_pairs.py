from flask import Blueprint, jsonify, request
from app.models.trade_pairs import TradePair
from app import db

bp = Blueprint('trade_pairs', __name__)


@bp.route('/', methods=['GET', 'POST'])
def get_trade_pairs():
    if request.method == 'GET':
        trade_pairs = TradePair.query.all()
        return jsonify([trade_pair.to_dict() for trade_pair in trade_pairs])
    elif request.method == 'POST':
        data = request.get_json()
        trade_pair = TradePair(name=data['name'])
        db.session.add(trade_pair)
        db.session.commit()



