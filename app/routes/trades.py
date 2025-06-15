from flask import Blueprint, jsonify, request
from app.models.signal import Signal
from app.routes.trades_association import (
    add_trade_associations,
    close_all_trade_associations,
    cancel_trade,
)
from app.models.prop_firm import PropFirm
from app.models.trade import Trade
from app import db
import json

# Create a Blueprint for the trades routes
bp = Blueprint("trades", __name__)


@bp.route("/<int:trade_id>", methods=["GET"])
def get_trade(trade_id):
    """Retrieve a specific trade by its ID.

    Args:
        trade_id (int): The ID of the signal to retrieve.

    Returns:
        JSON response containing the trade data or an error message if not found.
    """
    trade = db.session.get(Trade, trade_id)
    if not trade:
        return jsonify({"error": "Trade not found"}), 404
    return jsonify(trade.to_dict())


@bp.route("/", methods=["GET"], strict_slashes=False)
def handle_trades():
    """Handle GET requests for trades.

    GET: Retrieve all trades, ordered by ID in descending order.

    Returns:
        JSON response containing the list of trades or the status of the trade creation.
    """
    trades = db.session.query(Trade).order_by(Trade.signal_id.desc()).all()
    return jsonify({"trades": [trade.to_dict() for trade in trades]})


def handle_trade_with_parameters(saved_signal):
    """Handle a trade with parameters.

    Args:
        mt_string (str): The MT string to add the trade.
    """

    if saved_signal.position_size == 0:
        return close_all_trade_associations(saved_signal)
    else:
        try:
            trades = add_trade_associations(saved_signal)
            return jsonify(
                {"status": "success", "trades": [trade.signal_id for trade in trades]}
            )
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 400


@bp.route("/view", methods=["GET"])
def view_trades():
    """View trades along with their associated prop firms.

    Returns:
        JSON response containing trades with their associated prop firms.
    """
    trades_with_firms = (
        db.session.query(Trade, PropFirm)
        .select_from(Trade)
        .join(PropFirm, PropFirm.id == Trade.prop_firm_id)
        .order_by(Trade.signal_id.desc())
        .all()
    )

    result = []
    for trade, prop_firm in trades_with_firms:
        trade_data = trade.to_dict()
        trade_data["prop_firm"] = {
            "id": prop_firm.id,
            "name": prop_firm.name,
            "available_balance": prop_firm.available_balance,
            "drawdown_percentage": prop_firm.drawdown_percentage,
        }
        result.append(trade_data)

    return jsonify({"trades_with_firms": result})


@bp.route("/list", methods=["GET"])
def list_trades():
    """List all trades ordered by creation date with their prop firm details.

    Returns:
        JSON response containing the list of trades with response data.
    """
    trades = (
        db.session.query(Signal, Trade.response)
        .join(Trade)
        .order_by(Signal.created_at.desc())
        .all()
    )

    trades_with_response = []
    for trade, response in trades:
        trade_dict = trade.to_dict()
        if response:
            trade_dict["response"] = json.loads(response)
        else:
            trade_dict["response"] = None
        trades_with_response.append(trade_dict)

    return jsonify({"trades": trades_with_response})


@bp.route(
    "/<int:signal_id>/prop_firm/<int:prop_firm_id>",
    methods=["DELETE"],
    strict_slashes=False,
)
def delete_trade(signal_id, prop_firm_id):
    """Delete a specific trade by its ID.

    Args:
        signal_id (int): The ID of the signal to delete.
        prop_firm_id (int): The ID of the prop firm to delete.

    Returns:
        JSON response indicating the status of the deletion operation.
    """
    try:
        trade = Trade.query.filter_by(
            signal_id=signal_id,
            prop_firm_id=prop_firm_id,
        ).first()
        db.session.delete(trade)
        db.session.commit()
        return jsonify({"message": "Trade deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@bp.route("/<int:trade_id>/replay", methods=["POST"])
def replay_trade(trade_id):
    """Replay a specific trade by its ID.

    Args:
        trade_id (int): The ID of the trade to replay.

    Returns:
        JSON response indicating the status of the replay operation.
    """
    try:
        trade = Trade.query.get_or_404(trade_id)

        # Convert trade to MT string format
        mt_string = (
            f'"strategy":"{trade.strategy}", '
            f'"order":"{trade.order_type}", '
            f'"contracts":"{trade.contracts}", '
            f'"ticker":"{trade.ticker}", '
            f'"position_size":"{trade.position_size}"'
        )

        # Use the existing add_trade_associations function but without creating a new trade
        trades = add_trade_associations(mt_string, create_trade=False)

        return jsonify(
            {
                "status": "success",
                "message": "Trade replayed successfully",
                "trades": [trade.signal_id for trade in trades],
            }
        )
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@bp.route("/close", methods=["POST"])
def close_trade():
    """Close a specific trade identified by trade_id query parameter."""
    platform_id = request.get_json().get("platform_id")
    prop_firm_id = request.get_json().get("prop_firm_id")

    trade = Trade.query.filter_by(
        platform_id=platform_id,
        prop_firm_id=prop_firm_id,
    ).first()

    if not trade:
        return jsonify({"status": "error", "message": "Trade not found"}), 404

    prop_firm = PropFirm.query.filter_by(id=prop_firm_id).first()
    if not prop_firm:
        return jsonify({"status": "error", "message": "Prop firm not found"}), 404

    trade_id = cancel_trade(trade, prop_firm)
    return jsonify(
        {
            "status": "success",
            "message": "Trade closed successfully",
            "trade_id": trade_id,
        }
    )


@bp.route("/close_all_trades", methods=["GET"])
def close_all_trades():
    """Close all trades from all the prop firms associated with a trade.

    Returns:
        JSON response indicating the status of the close operation.
    """
    try:
        signal_id = request.args.get("signal_id")
        signal = Signal.query.get_or_404(signal_id)

        trades = close_all_trade_associations(signal)

        return (
            jsonify(
                {
                    "status": "success",
                    "message": "Trade closed successfully",
                    "trades": [trade.signal_id for trade in trades],
                }
            ),
            200,
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500
