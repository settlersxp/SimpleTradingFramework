from flask import Blueprint, jsonify, request
from app.models.prop_firm import PropFirm
from app import db
from app.models.trade_pairs import TradePairs
from app.models.trade import Trade
from app.models.prop_firm_trade_pair_association import (
    PropFirmTradePairAssociation,
)
from app.models.user import User
from app.routes.auth import login_required
from app.models.user import user_prop_firm
from sqlalchemy import select

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
            description=data.get("description"),
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
    user = User.get_user_by_token(
        request.headers.get("X-Session-ID"), request.headers.get("X-User-ID")
    )

    if not user:
        return jsonify({"error": "User not found"}), 404

    all_prop_firms = PropFirm.query.all()
    trade_associations = db.session.query(
        Trade.prop_firm_id,
        Trade.signal_id,
        Trade.platform_id,
        Trade.response,
    ).all()
    trade_map = {}
    for pf_id, t_id, plat_id, resp in trade_associations:
        if pf_id not in trade_map:
            trade_map[pf_id] = []
        trade_map[pf_id].append(
            {"trade_id": t_id, "platform_id": plat_id, "response": resp}
        )

    user_assoc_q = db.session.query(user_prop_firm.c.prop_firm_id).filter(
        user_prop_firm.c.user_id == user.id
    )
    assoc_pf_ids = {item[0] for item in user_assoc_q.all()}
    res_data = [
        {
            **pf.to_dict(),
            "is_active": pf.id in assoc_pf_ids,
            "trades": trade_map.get(pf.id, []),
            "description": pf.description,
        }
        for pf in all_prop_firms
    ]
    return jsonify(res_data)


@login_required
@bp.route("/<int:prop_firm_id>", methods=["DELETE", "GET"])
def delete_get_update_prop_firm(prop_firm_id):
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
    return jsonify(prop_firm.to_dict())


@login_required
@bp.route("/<int:prop_firm_id>/trades", methods=["GET"])
def trades_for_prop_firm(prop_firm_id):
    prop_firm = db.session.get(PropFirm, prop_firm_id)
    if not prop_firm:
        return jsonify({"error": "Prop firm not found"}), 404
    # Join trades with their corresponding signals so the frontend gets
    # all the information it needs (strategy, order_type, ticker …).
    assoc_q = db.session.query(Trade).filter_by(prop_firm_id=prop_firm_id)

    trades_data = []
    for assoc in assoc_q.all():
        # Each Trade row is linked to a Signal through the foreign-key relationship
        sig = assoc.signal  # SQLAlchemy relationship – may trigger lazy load
        if not sig:
            # In rare cases the signal might be missing; skip such rows
            continue

        # Combine Trade-level and Signal-level data in a single dict
        trade_data = {
            **sig.to_dict(),  # id, strategy, order_type, ticker …
            **assoc.to_dict(),  # platform_id, response, created_at …
        }

        trades_data.append(trade_data)

    output_data = prop_firm.to_dict()
    output_data["trades"] = trades_data
    return jsonify(output_data)


@login_required
@bp.route("/<int:prop_firm_id>", methods=["PUT"])
def update_prop_firm(prop_firm_id):
    try:
        data = request.get_json()
        prop_firm = db.session.get(PropFirm, prop_firm_id)
        user = User.get_user_by_token(
            request.headers.get("X-Session-ID"), request.headers.get("X-User-ID")
        )
        if not prop_firm:
            return jsonify({"error": "Prop firm not found"}), 404

        if "is_active" in data:
            if data["is_active"]:
                prop_firm.add_user(user)
            else:
                prop_firm.remove_user(user)

        if "name" in data:
            prop_firm.name = data["name"]
        if "full_balance" in data:
            prop_firm.full_balance = float(data["full_balance"])
        if "available_balance" in data:
            prop_firm.available_balance = float(data["available_balance"])
        if "drawdown_percentage" in data:
            prop_firm.drawdown_percentage = float(data["drawdown_percentage"])
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
        if "full_balance" in data:
            prop_firm.set_available_balance_to_full_balance()
            prop_firm.update_drawdown_percentage_on_full_balance_update(
                float(data["full_balance"])
            )
        if "description" in data:
            prop_firm.description = data["description"]
        db.session.commit()

        stmt = select(user_prop_firm).where(
            user_prop_firm.c.user_id == user.id,
            user_prop_firm.c.prop_firm_id == prop_firm.id,
        )
        is_associated = db.session.execute(stmt).first() is not None

        response_data = prop_firm.to_dict()
        response_data["is_active"] = is_associated

        return jsonify(
            {
                "status": "success",
                "message": "Prop firm updated successfully",
                "prop_firm": response_data,
            }
        )
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400


@login_required
@bp.route("/<int:prop_firm_id>/trade_pairs", methods=["GET", "POST"])
def manage_trade_pairs(prop_firm_id):
    prop_firm = db.session.get(PropFirm, prop_firm_id)
    if not prop_firm:
        return jsonify({"error": "Prop firm not found"}), 404
    if request.method == "GET":
        tp = TradePairs.query.all()
        curr_assoc_q = PropFirmTradePairAssociation.query.filter_by(
            prop_firm_id=prop_firm_id
        )
        curr_assoc_map = {ca.trade_pair_id: ca.label for ca in curr_assoc_q.all()}
        tp_data = [
            {
                "id": p.id,
                "name": p.name,
                "is_associated": p.id in curr_assoc_map,
                "current_label": curr_assoc_map.get(p.id, ""),
            }
            for p in tp
        ]
        return jsonify({"prop_firm": prop_firm.to_dict(), "trade_pairs": tp_data})
    elif request.method == "POST":
        try:
            data = request.get_json()
            assoc_data = data.get("associations", [])
            PropFirmTradePairAssociation.query.filter_by(
                prop_firm_id=prop_firm_id
            ).delete()
            for ad in assoc_data:
                new_assoc = PropFirmTradePairAssociation(
                    prop_firm_id=prop_firm_id,
                    trade_pair_id=ad["trade_pair_id"],
                    label=ad["label"],
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
@bp.route("/<int:prop_firm_id>/trade_pairs/<int:trade_pair_id>", methods=["DELETE"])
def delete_trade_pair(prop_firm_id, trade_pair_id):
    # Get the row with the given trade pair id and prop firm id
    trade_pair = PropFirmTradePairAssociation.query.filter_by(
        trade_pair_id=trade_pair_id, prop_firm_id=prop_firm_id
    ).first()
    if not trade_pair:
        return jsonify({"error": "Trade pair not found"}), 404
    try:
        db.session.delete(trade_pair)
        db.session.commit()
        return jsonify({"message": "Trade pair deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@login_required
@bp.route("/sync", methods=["POST"])
def sync_prop_firms():
    try:
        prop_firm_id_req = request.json.get("prop_firm_id") if request.json else None
        results = {}
        if prop_firm_id_req:
            pf_sync = PropFirm.query.get(prop_firm_id_req)
            if not pf_sync:
                return jsonify({"error": "Prop firm not found"}), 404
            results = pf_sync.trading.sync_prop_firm(pf_sync)
            msg = "Prop firm synced successfully"
            return jsonify(
                {
                    "prop_firm": results,
                    "success": True,
                    "message": msg,
                }
            )
        else:
            firms_to_sync = PropFirm.query.filter_by(is_active=True).all()
            for pf in firms_to_sync:
                results[pf.id] = pf.trading.sync_prop_firm(pf)
            s_count = sum(1 for r in results.values() if r)
            t_count = len(results)
            sync_msg = f"Synced {s_count} out of {t_count} prop firms"
            return jsonify(
                {
                    "success": True,
                    "message": sync_msg,
                    "results": results,
                }
            )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
