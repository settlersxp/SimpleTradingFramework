from flask import Blueprint, jsonify, request, render_template
from app.models.trade import Trade
from app.routes.trades_association import add_trade_associations
from app.models.prop_firm import PropFirm
from app.models.trade_association import prop_firm_trades
from app import db

bp = Blueprint('trades', __name__, url_prefix='/trades')


@bp.route('/<int:trade_id>', methods=['GET'])
def get_trade(trade_id):
    trade = db.session.get(Trade, trade_id)
    if not trade:
        return jsonify({"error": "Trade not found"}), 404
    return jsonify(trade.to_dict())


@bp.route('/', methods=['GET', 'POST'])
def trades():
    if request.method == 'GET':
        trades = db.session.query(Trade).order_by(Trade.id.desc()).all()
        return jsonify({
            "trades": [trade.to_dict() for trade in trades]
        })
    elif request.method == 'POST':
        mt_string = request.get_data(as_text=True)
        try:
            trade = add_trade_associations(mt_string)
            return jsonify({
                "status": "success",
                "trade_id": trade.id
            })
        except Exception as e:
            return jsonify({
                "status": "error",
                "message": str(e)
            }), 400


@bp.route('/view')
def view_trades():
    trades_with_firms = db.session.query(Trade, PropFirm)\
        .select_from(Trade)\
        .join(prop_firm_trades, Trade.id == prop_firm_trades.c.trade_id)\
        .join(PropFirm, PropFirm.id == prop_firm_trades.c.prop_firm_id)\
        .order_by(Trade.id.desc())\
        .all()
    return render_template('trades/view_trades.html', trades_with_firms=trades_with_firms)


@bp.route('/trades_associations', methods=['PUT'])
def update_trades_associations():
    try:
        data = request.get_json()
        
        # Extract data from request
        strategy = data.get('strategy')
        order_type = data.get('order')  # Note: 'order' in request maps to 'order_type' in model
        contracts = float(data.get('contracts'))
        ticker = data.get('ticker')
        position_size = float(data.get('position_size'))

        # Update all matching trades
        matching_trades = Trade.update_matching_trades(
            strategy=strategy,
            order_type=order_type,
            contracts=contracts,
            ticker=ticker,
            position_size=position_size
        )

        if not matching_trades:
            return jsonify({
                "status": "warning",
                "message": "No matching trades found"
            }), 200

        return jsonify({
            "status": "success",
            "message": f"Updated {len(matching_trades)} trades",
            "updated_trades": [trade.id for trade in matching_trades]
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 400


@bp.route('/list', methods=['GET'])
def list_trades():
    trades = Trade.query.order_by(Trade.created_at.desc()).all()
    return render_template('trades/list.html', trades=trades)


@bp.route('/<int:trade_id>', methods=['DELETE'])
def delete_trade(trade_id):
    try:
        trade = Trade.query.get_or_404(trade_id)
        db.session.delete(trade)
        db.session.commit()
        return jsonify({'message': 'Trade deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500