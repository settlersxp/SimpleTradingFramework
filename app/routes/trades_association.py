from flask import Blueprint, jsonify, request
from app.models.prop_firm import PropFirm
from app.models.trade import Trade
from app.models.trade_association import PropFirmTrades
from app.models.trade_pairs import TradePairs
from app.models.prop_firm_trade_pair_association import PropFirmTradePairAssociation
from app import db
from app.models.user import User
import json

bp = Blueprint('trades_association', __name__)


@staticmethod
def cancel_trade(trade, association, prop_firm):
    """Cancel a trade and remove its association with a prop firm.

    Args:
        trade (Trade): The trade to cancel.
        association: The association object linking the prop firm and trade pair.
        prop_firm (PropFirm): The prop firm associated with the trade.
    """
    # Find the trade in the trades table
    # Get all the associated prop firm trade pair associations
    # Get the platform id from the association
    old_trade = db.session.query(Trade).filter_by(
        order_type='buy' if trade.order_type == 'sell' else 'sell',
        ticker=trade.ticker,
        strategy=trade.strategy,
        contracts=trade.contracts,
    ).first()

    if not old_trade:
        return

    old_associations = db.session.query(PropFirmTrades).filter_by(
        trade_id=old_trade.id,
        prop_firm_id=association.prop_firm_id
    ).first()

    if not old_associations:
        return
    old_trade_response = json.loads(old_associations.response)
    outcome = prop_firm.trading.cancel_trade(old_trade_response)
    if outcome.success:
        old_associations.delete()
        Trade.query.filter_by(id=old_trade.id).delete()
        print(f"Trade {old_trade.id} canceled successfully")
        return old_trade.id
    else:
        print(f"Error canceling trade {old_trade.id}: {outcome.message}")
        return None


@staticmethod
def add_trade_associations(mt_string, create_trade=True):
    """Add trade associations based on the provided MT string.

    Args:
        mt_string (str): The MT string containing trade information.
        create_trade (bool): Flag indicating whether to create a new trade.

    Returns:
        [Trade]: One trade for each prop firm of each user.
    """
    trades = []
    trade = Trade.from_mt_string(mt_string)

    if create_trade:
        db.session.add(trade)
        db.session.commit()

    # Now we can directly use prop_firm as it has the association
    if trade.position_size == 0:
        # get the prop firms with this trade
        prop_firms = db.session.query(PropFirm).join(PropFirmTradePairAssociation).filter_by(trade_id=trade.id).all()
        for prop_firm in prop_firms:
            association = db.session.query(PropFirmTradePairAssociation).filter_by(
                prop_firm_id=prop_firm.id,
                trade_pair_id=trade.id
            ).first()
            trade_id = cancel_trade(trade, association, prop_firm)
            if trade_id:
                trades.append(trade_id)
        return trades

    # for every user in the database, get only the active prop firms
    all_users = db.session.query(User).all()
    for user in all_users:
        prop_firms = user.get_prop_firms()
        for prop_firm in prop_firms:
            # Check if the trade's ticker exists in trade_pairs
            trade_pair = db.session.query(
                TradePairs).filter_by(name=trade.ticker).first()

            if not trade_pair:
                print(f"Ticker {trade.ticker} not tracked by {prop_firm.name}")
                # If ticker is not tracked, skip prop firm associations
                continue

            # Check if the prop firm has an association with the trade pair
            association = db.session.query(PropFirmTradePairAssociation).filter_by(
                prop_firm_id=prop_firm.id,
                trade_pair_id=trade_pair.id
            ).first()

            if not association:
                print(f"Trade pair not associated with {trade.ticker} and {prop_firm.name}")
                continue

            # If association exists, use the label when placing the trade
            outcome = prop_firm.trading.place_trade(trade, label=association.label)
            if not outcome.success:
                print(f"Error placing trade {trade.id}: {outcome.message}")
                continue

            # Add trade to prop firm with platform ID
            prop_firm_trade = PropFirmTrades(
                prop_firm_id=prop_firm.id,
                trade_id=trade.id,
                platform_id=outcome.details['request_id'],
                response=json.dumps(outcome.details['response'])
            )
            db.session.add(prop_firm_trade)

            prop_firm.update_available_balance(trade)
            print(f"Trade {outcome.details['request_id']} placed successfully")
            trades.append(trade)

            db.session.commit()
    return trades



@bp.route('/', methods=['GET', 'POST', 'PUT'])
def trades_association():
    """Handle GET, POST, and PUT requests for trade associations.

    GET: Retrieve all trades associated with prop firms.
    POST: Create new trade associations from the provided data.
    PUT: Update existing trade associations based on the provided JSON data.

    Returns:
        JSON response containing trade association data or status messages.
    """
    if request.method == 'GET':
        # Query trades through PropFirmTrades association table
        trades_with_firms = db.session.query(Trade, PropFirm)\
            .select_from(Trade)\
            .join(PropFirmTrades, Trade.id == PropFirmTrades.c.trade_id)\
            .join(PropFirm, PropFirm.id == PropFirmTrades.c.prop_firm_id)\
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
            trades = add_trade_associations(mt_string)
            return jsonify({
                "status": "success",
                "trades": [trade.id for trade in trades]
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
            # Note: 'order' in request maps to 'order_type' in model
            order_type = data.get('order')
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
