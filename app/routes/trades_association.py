from flask import Blueprint, jsonify, request
from app.models.prop_firm import PropFirm
from app.models.trade import Trade
from app.models.trade_association import prop_firm_trades
from app import db

bp = Blueprint('trades_association', __name__)


@staticmethod
def add_trade_associations(mt_string):
    trade = Trade.from_mt_string(mt_string)
    db.session.add(trade)
    db.session.commit()

    # Add trade to all prop firms
    prop_firms = db.session.query(PropFirm).all()
    for prop_firm in prop_firms:
        prop_firm.trading.place_trade(trade)
        prop_firm.trades.append(trade)
        prop_firm.update_available_balance(trade)
    db.session.commit()
    return trade


@bp.route('/', methods=['GET', 'POST', 'PUT'])
def trades_association():
    if request.method == 'GET':
        # Query trades through prop_firm_trades association table
        trades_with_firms = db.session.query(Trade, PropFirm)\
            .select_from(Trade)\
            .join(prop_firm_trades, Trade.id == prop_firm_trades.c.trade_id)\
            .join(PropFirm, PropFirm.id == prop_firm_trades.c.prop_firm_id)\
            .order_by(Trade.created_at.desc())\
            .all()

        # Format the response to include both trade and prop firm info
        return jsonify([{
                **trade.to_dict(),
                "prop_firm": {
                    "id": prop_firm.id,
                    "name": prop_firm.name
                }
            } for trade, prop_firm in trades_with_firms])
    elif request.method == 'POST':
        try:
            mt_string = request.get_data(as_text=True)
            trade = add_trade_associations(mt_string)
            return jsonify({
                "status": "success",
                "trade_id": trade.id
            })
        except Exception as e:
            db.session.rollback()  # Rollback on error
            return jsonify({
                "status": "error",
                "message": str(e)
            }), 400
    elif request.method == 'PUT':
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
