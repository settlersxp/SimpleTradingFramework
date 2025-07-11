from flask import Blueprint, jsonify, request
from app.models.prop_firm import PropFirm
from app.models.signal import Signal
from app.models.trade import Trade
from app.models.trade_pairs import TradePairs
from app.models.prop_firm_trade_pair_association import PropFirmTradePairAssociation
from app import db
from app.models.user import User
import json
import logging

logger = logging.getLogger(__name__)

bp = Blueprint("trades_association", __name__)


def identify_old_trades(signal: Signal) -> list[Trade] | None:
    """Identify the old trade for a given signal.

    Args:
        signal (Signal): The signal to identify the old trade for.
    """
    old_signals = (
        db.session.query(Signal)
        .filter_by(
            order_type="buy" if signal.order_type == "sell" else "sell",
            ticker=signal.ticker,
            strategy=signal.strategy,
            contracts=signal.contracts,
        )
        .all()
    )

    if len(old_signals) == 0:
        logger.error(f"No old signal found for {signal.id}")
        return None

    old_trades = (
        db.session.query(Trade)
        .filter(Trade.signal_id.in_([signal.id for signal in old_signals]))
        .order_by(Trade.created_at.desc())
        .all()
    )

    if len(old_trades) == 0:
        logger.error(f"No old trade found for {signal.id}")
        return None

    return old_trades


@staticmethod
def cancel_trade(
    old_trade: Trade,
    prop_firm: PropFirm,
) -> int | None:
    """Cancel a trade and remove its association with a prop firm.

    Args:
        trade (Trade): The trade to cancel.
        association: The association object linking the prop firm and trade pair.
        prop_firm (PropFirm): The prop firm associated with the trade.
    """
    outcome = prop_firm.trading.cancel_trade(old_trade)

    if outcome.success:
        Trade.query.filter_by(
            platform_id=old_trade.platform_id,
            prop_firm_id=prop_firm.id,
            signal_id=old_trade.signal_id,
        ).delete()
        db.session.commit()
        logger.info(
            f"Trade {old_trade.ticker} {old_trade.platform_id} canceled successfully"
        )
        return old_trade.platform_id
    else:
        logger.error(
            f"Error canceling trade {old_trade.ticker} {old_trade.platform_id}: {outcome.message}"
        )
        return None


def close_all_trade_associations(signal: Signal):
    """Close all trade associations for a signal.

    Args:
        signal (Signal): The signal to close.
    """
    trades = []

    old_trades = identify_old_trades(signal)
    if not old_trades:
        logger.error(f"No old trade found for {signal.id}")
        return []

    for trade in old_trades:
        logger.info(f"Closing trade {trade.platform_id} for {trade.prop_firm.name}")
        trade_id = cancel_trade(trade, trade.prop_firm)
        if trade_id:
            trades.append(trade)
    return trades


@staticmethod
def add_trade_associations(saved_signal: Signal):
    """Add trade associations based on the provided MT string.

    Args:
        saved_signal (Signal): The signal to add trade associations for.

    Returns:
        [Trade]: One trade for each prop firm of each user.
    """
    trades = []

    # for every user in the database, get only the active prop firms
    all_users = db.session.query(User).all()
    for user in all_users:
        prop_firms = user.get_prop_firms()
        for prop_firm in prop_firms:
            # Check if the trade's ticker exists in trade_pairs
            trade_pair = (
                db.session.query(TradePairs).filter_by(name=saved_signal.ticker).first()
            )

            if not trade_pair:
                print(f"Ticker {saved_signal.ticker} not tracked by {prop_firm.name}")
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
                    f"Trade pair not associated with {saved_signal.ticker} and {prop_firm.name}"
                )
                continue

            print(f"Current prop firm {prop_firm.name}")
            # If association exists, use the label when placing the trade
            outcome = prop_firm.trading.place_trade(
                saved_signal, label=association.label
            )
            if not outcome.success:
                print(f"Error placing trade: {outcome.message}")
                continue

            # Add trade to prop firm with platform ID
            prop_firm_trade = Trade.associate_signal(
                signal=saved_signal,
                prop_firm=prop_firm,
                platform_id=outcome.details["response"].ticket,
                response=json.dumps(outcome.details["response"]._asdict()),
                ticker=association.label,
            )

            prop_firm.update_available_balance(saved_signal)
            print(f"Trade {outcome.details['response'].ticket} placed successfully")
            trades.append(prop_firm_trade)
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
