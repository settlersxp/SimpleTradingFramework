from flask import Blueprint, jsonify, request, render_template
from app.models.trade import Trade
from app.routes.trades_association import add_trade_associations
from app.models.prop_firm import PropFirm
from app.models.trade_association import prop_firm_trades
from app import db

# Create a Blueprint for the trades routes
bp = Blueprint('trades', __name__, url_prefix='/trades')


@bp.route('/<int:trade_id>', methods=['GET'])
def get_trade(trade_id):
    """Retrieve a specific trade by its ID.

    Args:
        trade_id (int): The ID of the trade to retrieve.

    Returns:
        JSON response containing the trade data or an error message if not found.
    """
    trade = db.session.get(Trade, trade_id)
    if not trade:
        return jsonify({"error": "Trade not found"}), 404
    return jsonify(trade.to_dict())


@bp.route('/', methods=['GET', 'POST'])
def trades():
    """Handle GET and POST requests for trades.

    GET: Retrieve all trades, ordered by ID in descending order.
    POST: Create a new trade association from the request data.

    Returns:
        JSON response containing the list of trades or the status of the trade creation.
    """
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
    """View trades along with their associated prop firms.

    Returns:
        Rendered HTML template displaying trades with their associated prop firms.
    """
    trades_with_firms = db.session.query(Trade, PropFirm)\
        .select_from(Trade)\
        .join(prop_firm_trades, Trade.id == prop_firm_trades.c.trade_id)\
        .join(PropFirm, PropFirm.id == prop_firm_trades.c.prop_firm_id)\
        .order_by(Trade.id.desc())\
        .all()
    return render_template('trades/view_trades.html', trades_with_firms=trades_with_firms)


@bp.route('/trades_associations', methods=['PUT'])
def update_trades_associations():
    """Update existing trade associations based on the provided JSON data.

    Returns:
        JSON response indicating the status of the update operation.
    """
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


@bp.route('/list', methods=['GET'])
def list_trades():
    """List all trades ordered by creation date.

    Returns:
        Rendered HTML template displaying the list of trades.
    """
    trades = Trade.query.order_by(Trade.created_at.desc()).all()
    return render_template('trades/list.html', trades=trades)


@bp.route('/<int:trade_id>', methods=['DELETE'])
def delete_trade(trade_id):
    """Delete a specific trade by its ID.

    Args:
        trade_id (int): The ID of the trade to delete.

    Returns:
        JSON response indicating the status of the deletion operation.
    """
    try:
        trade = Trade.query.get_or_404(trade_id)
        db.session.delete(trade)
        db.session.commit()
        return jsonify({'message': 'Trade deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:trade_id>/replay', methods=['POST'])
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
        add_trade_associations(mt_string, create_trade=False)
        
        return jsonify({
            "status": "success",
            "message": "Trade replayed successfully"
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@bp.route('/close', methods=['GET'])
def close_trade():
    """Close a specific trade identified by trade_id query parameter.

    Returns:
        JSON response indicating the status of the close operation.
    """
    try:
        trade_id = request.args.get('trade_id')
        trade = Trade.query.get_or_404(trade_id)
        
        # Convert trade to MT string format with close order
        mt_string = (
            f'"strategy":"{trade.strategy}", '
            f'"order":"{trade.order_type}", '
            f'"contracts":"{trade.contracts}", '
            f'"ticker":"{trade.ticker}", '
            f'"position_size":"{trade.position_size}"'
        )
        
        add_trade_associations(mt_string, create_trade=False)
        
        return jsonify({'message': 'Trade closed successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
