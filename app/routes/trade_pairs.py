from flask import Blueprint, jsonify, request, render_template
from app import db
from app.models.trade_pairs import TradePairs

bp = Blueprint('trade_pairs', __name__ )


@bp.route('/', methods=['GET'])
def index():
    """Render the index page for trade pairs.

    Returns:
        Rendered HTML template displaying all trade pairs.
    """
    trade_pairs = TradePairs.query.all()
    return render_template('trade_pairs/index.html', trade_pairs=trade_pairs)


@bp.route('/pairs', methods=['GET', 'POST', 'PUT', 'DELETE'])
def handle_pairs():
    """Handle requests for trade pairs.

    GET: Retrieve all trade pairs.
    POST: Create a new trade pair.
    PUT: Update an existing trade pair.
    DELETE: Remove a trade pair.

    Returns:
        JSON response containing trade pair data or status messages.
    """
    if request.method == 'GET':
        # Retrieve all trade pairs and return as JSON
        trade_pairs = TradePairs.query.all()
        return jsonify([pair.to_dict() for pair in trade_pairs])
    elif request.method == 'POST':
        # Create a new trade pair from the request data
        data = request.get_json()
        trade_pair = TradePairs(name=data['name'])
        db.session.add(trade_pair)
        db.session.commit()
        return jsonify(trade_pair.to_dict()), 201
    elif request.method == 'PUT':
        # Update an existing trade pair based on the provided ID
        data = request.get_json()
        trade_pair = TradePairs.query.get_or_404(data['id'])
        trade_pair.name = data['name']
        db.session.commit()
        return jsonify(trade_pair.to_dict())
    elif request.method == 'DELETE':
        # Delete a trade pair based on the provided ID
        data = request.get_json()
        trade_pair = TradePairs.query.get_or_404(data['id'])
        db.session.delete(trade_pair)
        db.session.commit()
        return '', 204
