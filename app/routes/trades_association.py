from flask import Blueprint, jsonify, request
from app.models.prop_firm import PropFirm
from app.models.signal import Signal
from app.models.trade import Trade
from app.models.trade_pairs import TradePairs
from app.models.prop_firm_trade_pair_association import PropFirmTradePairAssociation
from app import db
from app.models.user import User
import json

bp = Blueprint("trades_association", __name__)


def identify_old_trade(trade):
    """Identify the old trade for a given trade.

    Args:
        trade (Signal): The trade to identify the old trade for.
    """
    old_trade = (
        db.session.query(Signal)
        .filter_by(
            order_type="buy" if trade.order_type == "sell" else "sell",
            ticker=trade.ticker,
            strategy=trade.strategy,
            contracts=trade.contracts,
        )
        .first()
    )
    return old_trade


@staticmethod
def cancel_trade(old_trade, association, prop_firm):
    """Cancel a trade and remove its association with a prop firm.

    Args:
        trade (Trade): The trade to cancel.
        association: The association object linking the prop firm and trade pair.
        prop_firm (PropFirm): The prop firm associated with the trade.
    """
    old_trade_response = json.loads(association.response)
    outcome = prop_firm.trading.cancel_trade(old_trade_response)

    if outcome.success:
        # association.delete()
        # Trade.query.filter_by(id=old_trade.id).delete()
        print(f"Trade {old_trade.id} canceled successfully")
        return old_trade.id
    else:
        print(f"Error canceling trade {old_trade.id}: {outcome.message}")
        return None


def close_all_trade_associations(trade):
    """Close all trade associations for a trade.

    Args:
        trade (Trade): The trade to close.
    """
    trades = []

    old_trade = identify_old_trade(trade)
    if not old_trade:
        print(f"No old trade found for {trade.id}")
        return []

    prop_firms = (
        db.session.query(PropFirm)
        .join(Trade)
        .filter_by(signal_id=old_trade.id)
        .all()
    )

    for prop_firm in prop_firms:
        associations = prop_firm.get_trade_associations()
        if not associations:
            continue

        for association in associations:
            if not association.trade_id:
                print(f"No trade id found for {association.platform_id}")
                continue

            print(f"Closing trade {association.platform_id} for {prop_firm.name}")
            trade_id = cancel_trade(old_trade, association, prop_firm)
            if trade_id:
                trades.append(trade_id)
    return trades


def add_trade_associations(mt_string, create_trade=True):
    """Add trade associations based on the provided MT string.

    Args:
        mt_string (str): The MT string containing trade information.
        create_trade (bool): Flag indicating whether to create a new trade.

    Returns:
        [Trade]: One trade for each prop firm of each user.
    """
    trades = []
    trade = Signal.from_mt_string(mt_string)

    if create_trade:
        db.session.add(trade)
        db.session.commit()

    # Now we can directly use prop_firm as it has the association
    if trade.position_size == 0:
        # get the prop firms with this trade
        trades = close_all_trade_associations(trade)
        return trades

    # for every user in the database, get only the active prop firms
    all_users = db.session.query(User).all()
    for user in all_users:
        prop_firms = user.get_prop_firms()
        for prop_firm in prop_firms:
            # Check if the trade's ticker exists in trade_pairs
            trade_pair = (
                db.session.query(TradePairs).filter_by(name=trade.ticker).first()
            )

            if not trade_pair:
                print(f"Ticker {trade.ticker} not tracked by {prop_firm.name}")
                # If ticker is not tracked, skip prop firm associations
                continue

            # Check if the prop firm has an association with the trade pair
            association = (
                db.session.query(PropFirmTradePairAssociation)
                .filter_by(prop_firm_id=prop_firm.id, trade_pair_id=trade_pair.id)
                .first()
            )

            if not association:
                print(
                    f"Trade pair not associated with {trade.ticker} and {prop_firm.name}"
                )
                continue

            print(f"Current prop firm {prop_firm.name}")
            # If association exists, use the label when placing the trade
            outcome = prop_firm.trading.place_trade(trade, label=association.label)
            if not outcome.success:
                print(f"Error placing trade {trade.id}: {outcome.message}")
                continue

            # Add trade to prop firm with platform ID
            prop_firm_trade = Trade(
                prop_firm_id=prop_firm.id,
                signal_id=trade.id,
                platform_id=outcome.details["request_id"],
                response=json.dumps(outcome.details["response"]),
            )
            db.session.add(prop_firm_trade)

            prop_firm.update_available_balance(trade)
            print(f"Trade {outcome.details['request_id']} placed successfully")
            trades.append(trade)

            db.session.commit()
    return trades


@bp.route("/", methods=["GET", "POST", "PUT"])
def trades_association():
    """Handle GET, POST, and PUT requests for trade associations.

    GET: Retrieve all trades associated with prop firms.
    POST: Create new trade associations from the provided data.
    PUT: Update existing trade associations based on the provided JSON data.

    Returns:
        JSON response containing trade association data or status messages.
    """
    if request.method == "GET":
        # Query trades through Trades table
        trades_with_firms = (
            db.session.query(Signal, PropFirm)
            .select_from(Signal)
            .join(Trade, Signal.id == Trade.signal_id)
            .join(PropFirm, PropFirm.id == Trade.prop_firm_id)
            .order_by(Signal.created_at.desc())
            .all()
        )

        # Format the response to include both trade and prop firm info
        return jsonify(
            [
                {
                    **trade.to_dict(),
                    "prop_firm": {"id": prop_firm.id, "name": prop_firm.name},
                }
                for trade, prop_firm in trades_with_firms
            ]
        )
    elif request.method == "POST":
        try:
            mt_string = request.get_data(as_text=True)
            trades = add_trade_associations(mt_string)
            return jsonify(
                {"status": "success", "trades": [trade.id for trade in trades]}
            )
        except Exception as e:
            db.session.rollback()  # Rollback on error
            return jsonify({"status": "error", "message": str(e)}), 400
    elif request.method == "PUT":
        try:
            data = request.get_json()

            # Extract data from request
            strategy = data.get("strategy")
            # Note: 'order' in request maps to 'order_type' in model
            order_type = data.get("order")
            contracts = float(data.get("contracts"))
            ticker = data.get("ticker")
            position_size = float(data.get("position_size"))

            # Update all matching trades
            matching_trades = Signal.update_matching_trades(
                strategy=strategy,
                order_type=order_type,
                contracts=contracts,
                ticker=ticker,
                position_size=position_size,
            )

            if not matching_trades:
                return (
                    jsonify(
                        {"status": "warning", "message": "No matching trades found"}
                    ),
                    200,
                )

            return jsonify(
                {
                    "status": "success",
                    "message": f"Updated {len(matching_trades)} trades",
                    "updated_trades": [trade.id for trade in matching_trades],
                }
            )

        except Exception as e:
            db.session.rollback()
            return jsonify({"status": "error", "message": str(e)}), 400
