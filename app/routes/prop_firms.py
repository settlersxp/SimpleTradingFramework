from flask import Blueprint, jsonify, request
from app.models.prop_firm import PropFirm
from app import db
from app.models.trade_pairs import TradePairs
from app.models.trade_association import PropFirmTrades
from app.models.prop_firm_trade_pair_association import PropFirmTradePairAssociation
from app.routes.auth import login_required

bp = Blueprint("prop_firms", __name__)


@login_required
@bp.route("/create", methods=["POST"])
def create_prop_firm():
    """
    Create a new prop firm.
    POST: Create a new prop firm.
    """
    try:
        data = request.get_json()

        # Create a new prop firm
        prop_firm = PropFirm(
            name=data.get("name"),
            full_balance=float(data.get("full_balance", 0)),
            available_balance=float(data.get("available_balance", 0)),
            drawdown_percentage=float(data.get("drawdown_percentage", 0)),
            is_active=data.get("is_active", False),
            username=data.get("username"),
            password=data.get("password"),
            ip_address=data.get("ip_address"),
            port=data.get("port"),
            platform_type=data.get("platform_type"),
        )

        db.session.add(prop_firm)
        db.session.commit()

        return (
            jsonify(
                {
                    "status": "success",
                    "message": "Prop firm created successfully",
                    "prop_firm": prop_firm.to_dict(),
                }
            ),
            201,
        )
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 400


@login_required
@bp.route("/", methods=["GET"])
def get_prop_firms():
    """
    Get all prop firms.
    GET: Get all prop firms and their trade associations.
    """
    # First query: Get all prop firms
    prop_firms = PropFirm.query.all()

    # Second query: Get all trade associations
    associations = db.session.query(
        PropFirmTrades.prop_firm_id,
        PropFirmTrades.trade_id,
        PropFirmTrades.platform_id,
        PropFirmTrades.response,
    ).all()

    # Create a dictionary to group trade associations by prop firm
    trade_map = {}
    for assoc in associations:
        prop_firm_id = assoc.prop_firm_id
        if prop_firm_id not in trade_map:
            trade_map[prop_firm_id] = []

        trade_map[prop_firm_id].append(
            {
                "trade_id": assoc.trade_id,
                "platform_id": assoc.platform_id,
                "response": assoc.response,
            }
        )

    # Build response with combined data
    return jsonify(
        [
            {
                "id": pf.id,
                "name": pf.name,
                "full_balance": pf.full_balance,
                "available_balance": pf.available_balance,
                "drawdown_percentage": pf.drawdown_percentage,
                "username": pf.username,
                "password": pf.password,
                "ip_address": pf.ip_address,
                "port": pf.port,
                "platform_type": pf.platform_type,
                "is_active": pf.is_active,
                "created_at": pf.created_at.isoformat() if pf.created_at else None,
                "trades": trade_map.get(pf.id, []),
            }
            for pf in prop_firms
        ]
    )


@login_required
@bp.route("/<int:prop_firm_id>", methods=["DELETE", "GET"])
def delete_get_update_prop_firm(prop_firm_id):
    """
    Delete or get/update a prop firm.
    DELETE: Delete a prop firm.
    GET: Get a prop firm.
    """
    prop_firm = db.session.get(PropFirm, prop_firm_id)
    if not prop_firm:
        return jsonify({"error": "Prop firm not found"}), 404

    if request.method == "DELETE":
        try:
            db.session.delete(prop_firm)
            db.session.commit()
            return jsonify({"message": "Prop firm deleted successfully"}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500

    # GET method
    return jsonify(prop_firm.to_dict())


@login_required
@bp.route("/<int:prop_firm_id>/trades", methods=["GET"])
def trades_for_prop_firm(prop_firm_id):
    """
    Get all trades associated with a prop firm.
    GET: Get all trades and their associations.
    """
    prop_firm = db.session.get(PropFirm, prop_firm_id)
    if not prop_firm:
        return jsonify({"error": "Prop firm not found"}), 404

    # Get all trades associated with this prop firm
    associations = (
        db.session.query(PropFirmTrades).filter_by(prop_firm_id=prop_firm_id).all()
    )

    trades_data = []
    for assoc in associations:
        trade = assoc.trade
        if not trade:
            continue

        trade_data = trade.to_dict()
        trade_data["platform_id"] = assoc.platform_id
        trade_data["response"] = assoc.response
        trades_data.append(trade_data)

    return jsonify({"prop_firm": prop_firm.to_dict(), "trades": trades_data})


@login_required
@bp.route("/<int:prop_firm_id>", methods=["PUT"])
def update_prop_firm(prop_firm_id):
    try:
        data = request.get_json()

        prop_firm = db.session.get(PropFirm, prop_firm_id)
        if not prop_firm:
            return jsonify({"error": "Prop firm not found"}), 404

        # Update fields if provided
        if "name" in data:
            prop_firm.name = data["name"]
        if "full_balance" in data:
            prop_firm.full_balance = float(data["full_balance"])
        if "available_balance" in data:
            prop_firm.available_balance = float(data["available_balance"])
        if "drawdown_percentage" in data:
            prop_firm.drawdown_percentage = float(data["drawdown_percentage"])
        if "is_active" in data:
            prop_firm.is_active = data["is_active"]
        if "username" in data:
            prop_firm.username = data["username"]
        if "password" in data:
            prop_firm.password = data["password"]
        if "ip_address" in data:
            prop_firm.ip_address = data["ip_address"]
        if "port" in data:
            prop_firm.port = data["port"]
        if "platform_type" in data:
            prop_firm.platform_type = data["platform_type"]

        # Update downdraft percentage if full balance changed
        if "full_balance" in data:
            prop_firm.set_available_balance_to_full_balance()
            prop_firm.update_drawdown_percentage_on_full_balance_update(
                float(data["full_balance"])
            )

        db.session.commit()

        return jsonify(
            {
                "status": "success",
                "message": "Prop firm updated successfully",
                "prop_firm": prop_firm.to_dict(),
            }
        )
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400


@login_required
@bp.route("/<int:prop_firm_id>/trade_pairs", methods=["GET", "POST"])
def manage_trade_pairs(prop_firm_id):
    """
    Manage trade pairs for a prop firm.
    GET: Get all trade pairs and their associations.
    POST: Update the associations for a prop firm.
    """
    prop_firm = db.session.get(PropFirm, prop_firm_id)
    if not prop_firm:
        return jsonify({"error": "Prop firm not found"}), 404

    if request.method == "GET":
        # Get all trade pairs
        trade_pairs = TradePairs.query.all()

        # Get current associations
        current_associations = PropFirmTradePairAssociation.query.filter_by(
            prop_firm_id=prop_firm_id
        ).all()

        # Create a dict of current associations for easy lookup
        current_assoc_dict = {
            assoc.trade_pair_id: assoc.label for assoc in current_associations
        }

        # Format response
        trade_pairs_data = []
        for pair in trade_pairs:
            is_associated = pair.id in current_assoc_dict
            trade_pairs_data.append(
                {
                    "id": pair.id,
                    "name": pair.name,
                    "is_associated": is_associated,
                    "current_label": current_assoc_dict.get(pair.id, ""),
                }
            )

        return jsonify(
            {"prop_firm": prop_firm.to_dict(), "trade_pairs": trade_pairs_data}
        )

    elif request.method == "POST":
        try:
            data = request.get_json()
            associations = data.get("associations", [])

            # Remove all existing associations
            PropFirmTradePairAssociation.query.filter_by(
                prop_firm_id=prop_firm_id
            ).delete()

            # Add new associations
            for assoc in associations:
                new_assoc = PropFirmTradePairAssociation(
                    prop_firm_id=prop_firm_id,
                    trade_pair_id=assoc["trade_pair_id"],
                    label=assoc["label"],
                )
                db.session.add(new_assoc)

            db.session.commit()

            return jsonify(
                {
                    "status": "success",
                    "message": "Trade pair associations updated successfully",
                }
            )
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 400


@login_required
@bp.route("/sync", methods=["POST"])
def sync_prop_firms():
    """
    Synchronize all active prop firms with MT5.
    Updates account information and creates new trades.
    """
    try:
        # Get prop firm ID from request if specified
        prop_firm_id = request.json.get("prop_firm_id") if request.json else None

        if prop_firm_id:
            # Sync specific prop firm
            prop_firm = PropFirm.query.get(prop_firm_id)
            if not prop_firm:
                return jsonify({"error": "Prop firm not found"}), 404

            result = prop_firm.trading.sync_prop_firm(prop_firm)
            return jsonify(
                {
                    "prop_firm": result,
                    "success": True,
                    "message": "Prop firm synced successfully",
                }
            )
        else:
            # Sync all active prop firms
            prop_firms = PropFirm.query.filter_by(is_active=True).all()
            results = {}
            for prop_firm in prop_firms:
                result = prop_firm.trading.sync_prop_firm(prop_firm)
                results[prop_firm.id] = result

            # Count successes and failures
            success_count = sum(1 for success in results.values() if success)
            total_count = len(results)

            return jsonify(
                {
                    "success": True,
                    "message": f"Synced {success_count} out of {total_count} prop firms",
                    "results": results,
                }
            )

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
