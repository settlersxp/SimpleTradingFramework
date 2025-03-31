from flask import Blueprint, jsonify, request
from app import db
from app.models.trading_strategy import TradingStrategy
from app.models.user import User
from app.routes.auth import login_required

bp = Blueprint("trading_strategies", __name__)


@login_required
@bp.route("/", methods=["GET"])
def get_all_trading_strategies():
    """Get all trading strategies"""
    try:
        strategies = TradingStrategy.query.all()
        return jsonify([strategy.to_dict() for strategy in strategies])
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@login_required
@bp.route("/<int:strategy_id>", methods=["GET"])
def get_trading_strategy(strategy_id):
    """Get a specific trading strategy by ID"""
    try:
        strategy = db.session.get(TradingStrategy, strategy_id)
        if not strategy:
            return jsonify({"error": "Trading strategy not found"}), 404
        return jsonify(strategy.to_dict())
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@login_required
@bp.route("/", methods=["POST"])
def create_trading_strategy():
    """Create a new trading strategy"""
    try:
        data = request.get_json()

        # Check if a strategy with this name already exists
        existing = TradingStrategy.query.filter_by(name=data.get("name")).first()
        if existing:
            return (
                jsonify(
                    {
                        "error": f"A strategy with the name '{data.get('name')}' already exists"
                    }
                ),
                400,
            )

        # Create a new trading strategy
        strategy = TradingStrategy(
            name=data.get("name"), description=data.get("description")
        )

        db.session.add(strategy)
        db.session.commit()

        return (
            jsonify(
                {
                    "status": "success",
                    "message": "Trading strategy created successfully",
                    "strategy": strategy.to_dict(),
                }
            ),
            201,
        )
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@login_required
@bp.route("/<int:strategy_id>", methods=["PUT"])
def update_trading_strategy(strategy_id):
    """Update an existing trading strategy"""
    try:
        data = request.get_json()
        strategy = db.session.get(TradingStrategy, strategy_id)

        if not strategy:
            return jsonify({"error": "Trading strategy not found"}), 404

        # Check if name is being changed and if the new name already exists
        if "name" in data and data["name"] != strategy.name:
            existing = TradingStrategy.query.filter_by(name=data["name"]).first()
            if existing:
                return (
                    jsonify(
                        {
                            "error": f"A strategy with the name '{data['name']}' already exists"
                        }
                    ),
                    400,
                )
            strategy.name = data["name"]

        if "description" in data:
            strategy.description = data["description"]

        db.session.commit()

        return jsonify(
            {
                "status": "success",
                "message": "Trading strategy updated successfully",
                "strategy": strategy.to_dict(),
            }
        )
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@login_required
@bp.route("/<int:strategy_id>", methods=["DELETE"])
def delete_trading_strategy(strategy_id):
    """Delete a trading strategy"""
    try:
        strategy = db.session.get(TradingStrategy, strategy_id)

        if not strategy:
            return jsonify({"error": "Trading strategy not found"}), 404

        db.session.delete(strategy)
        db.session.commit()

        return jsonify(
            {"status": "success", "message": "Trading strategy deleted successfully"}
        )
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@login_required
@bp.route("/user/<int:user_id>", methods=["GET"])
def get_user_trading_strategies(user_id):
    """Get all trading strategies associated with a user"""
    try:
        user = db.session.get(User, user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404

        strategies = user.get_trading_strategies()
        return jsonify([strategy.to_dict() for strategy in strategies])
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@login_required
@bp.route("/user/<int:user_id>/associate", methods=["POST"])
def associate_user_with_strategies(user_id):
    """Associate a user with multiple trading strategies"""
    try:
        data = request.get_json()

        if "strategy_ids" not in data:
            return jsonify({"error": "strategy_ids is required"}), 400

        user = db.session.get(User, user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404

        # Clear existing associations
        if data.get("clear_existing", False):
            for strategy in user.get_trading_strategies():
                user.remove_trading_strategy(strategy)

        # Add new associations
        added_strategies = []
        for strategy_id in data["strategy_ids"]:
            strategy = db.session.get(TradingStrategy, strategy_id)
            if strategy:
                if user.add_trading_strategy(strategy):
                    added_strategies.append(strategy.to_dict())

        db.session.commit()

        return jsonify(
            {
                "status": "success",
                "message": f"User associated with {len(added_strategies)} trading strategies",
                "strategies": added_strategies,
            }
        )
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
