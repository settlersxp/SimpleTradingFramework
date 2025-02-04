from flask import Blueprint, jsonify, request, render_template
from app.models.prop_firm import PropFirm
from app import db

bp = Blueprint('prop_firms', __name__, url_prefix='/prop_firms')


@bp.route('/', methods=['GET', 'POST'])
def create_and_get_prop_firms():
    if request.method == 'GET':
        prop_firms = db.session.query(PropFirm).all()
        return jsonify([{
                "id": pf.id,
                "name": pf.name,
                "full_balance": pf.full_balance,
                "available_balance": pf.available_balance,
                "dowdown_percentage": pf.dowdown_percentage,
                "trades": [t.id for t in pf.trades]
            } for pf in prop_firms])
    elif request.method == 'POST':
        # create a new prop firm
        data = request.get_json()
        data['platform_type'] = 'MT5'
        prop_firm = PropFirm(**data)
        prop_firm.set_available_balance_to_full_balance()
        db.session.add(prop_firm)
        db.session.commit()
        return jsonify({
            "status": "success",
            "prop_firm_id": prop_firm.id
        })    


@bp.route('/<int:prop_firm_id>', methods=['DELETE', 'GET'])
def delete_get_update_prop_firm(prop_firm_id):
    prop_firm = db.session.get(PropFirm, prop_firm_id)
    if not prop_firm:
        return jsonify({
            "status": "error",
            "message": "Prop firm not found"
        }), 404

    if request.method == 'DELETE':
        try:
            if prop_firm:
                db.session.delete(prop_firm)
                db.session.commit()
                return jsonify({
                    "status": "success"
                })
        except Exception as e:
            db.session.rollback()
            return jsonify({
                "status": "error",
                "message": str(e)
            }), 400
    elif request.method == 'GET':
        return jsonify(prop_firm.to_dict())


@bp.route('/<int:prop_firm_id>/trades', methods=['GET'])
def trades_for_prop_firm(prop_firm_id):
    # Should look like /prop_firm/3/trades
    try:
        prop_firm = db.session.get(PropFirm, prop_firm_id)
        if not prop_firm:
            return jsonify({
                "status": "error",
                "message": "Prop firm not found"
            }), 404
        return jsonify({
                "prop_firm_id": prop_firm.id,
                "prop_firm_name": prop_firm.name,
                "trades": [{
                    "trade_id": t.id,
                    "strategy": t.strategy,
                    "order_type": t.order_type,
                    "contracts": t.contracts,
                    "ticker": t.ticker,
                    "position_size": t.position_size,
                    "created_at": t.created_at.isoformat()
                } for t in prop_firm.trades]
            })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 400


@bp.route('/view')
def view_prop_firms():
    prop_firms = PropFirm.query.all()
    return render_template('prop_firms/prop_firms.html', prop_firms=prop_firms)


@bp.route('/view/<int:prop_firm_id>/edit')
def edit_prop_firm(prop_firm_id):
    prop_firm = db.session.get(PropFirm, prop_firm_id)
    if not prop_firm:
        return "Prop Firm not found", 404
    return render_template('prop_firms/edit_prop_firm.html', prop_firm=prop_firm)

@bp.route('/<int:prop_firm_id>', methods=['PUT'])
def update_prop_firm(prop_firm_id):
    # a for or a JSON object can be received
    if request.method == 'POST':
        received_data = request.form.to_dict()
    elif request.method == 'PUT':
        received_data = request.get_json()

    # update an existing prop firm with the data received from the request
    try:
        db_prop_firm = db.session.get(PropFirm, prop_firm_id)
        if not db_prop_firm:
            return jsonify({"status": "error", "message": "Prop firm not found"}), 404

        # Update the prop firm attributes
        db_prop_firm.name = received_data.get('name', request.form.get('name'))
        db_prop_firm.full_balance = float(received_data.get('full_balance', request.form.get('full_balance')))
        db_prop_firm.username = received_data.get('username', request.form.get('username'))
        db_prop_firm.password = received_data.get('password', request.form.get('password'))
        db_prop_firm.ip_address = received_data.get('ip_address', request.form.get('ip_address'))
        db_prop_firm.port = int(received_data.get('port', request.form.get('port')))
        db_prop_firm.platform_type = received_data.get('platform_type', request.form.get('platform_type'))
        db_prop_firm.is_active = received_data.get('is_active', request.form.get('is_active'))
        
        # Update downdraft percentage if full balance changed
        if 'full_balance' in received_data:
            db_prop_firm.set_available_balance_to_full_balance()
            db_prop_firm.update_dowdown_percentage_on_full_balance_update(float(received_data['full_balance']))
        
        db.session.commit()
        
        return jsonify({
            "status": "success",
            "message": "Prop firm updated successfully"
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 400
