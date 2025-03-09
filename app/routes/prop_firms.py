from flask import Blueprint, jsonify, request, render_template, redirect, url_for, flash
from app.models.prop_firm import PropFirm
from app import db
from app.forms.prop_firm import PropFirmForm
from app.models.trade_pairs import TradePairs
from app.models.trade_association import PropFirmTrades

bp = Blueprint('prop_firms', __name__, url_prefix='/prop_firms')


@bp.route('/', methods=['GET', 'POST'])
def create_and_get_prop_firms():
    if request.method == 'GET':
        # First query: Get all prop firms
        prop_firms = PropFirm.query.all()
        
        # Second query: Get all trade associations using PropFirmTrades model
        associations = db.session.query(
            PropFirmTrades.prop_firm_id,
            PropFirmTrades.trade_id,
            PropFirmTrades.platform_id,
            PropFirmTrades.response
        ).all()
        
        # Create a dictionary to group trade associations by prop firm
        trade_map = {}
        for assoc in associations:
            prop_firm_id = assoc.prop_firm_id
            if prop_firm_id not in trade_map:
                trade_map[prop_firm_id] = []
            
            trade_map[prop_firm_id].append({
                "trade_id": assoc.trade_id,
                "platform_id": assoc.platform_id,
                "response": assoc.response
            })
        
        # Build response with combined data
        return jsonify([{
            "id": pf.id,
            "name": pf.name,
            "full_balance": pf.full_balance,
            "available_balance": pf.available_balance,
            "dowdown_percentage": pf.dowdown_percentage,
            "trades": trade_map.get(pf.id, [])
        } for pf in prop_firms])
    elif request.method == 'POST':
        try:
            # Handle both JSON and form data
            if request.is_json:
                data = request.get_json()
            else:
                data = request.form.to_dict()
                # Convert string values to appropriate types
                if 'full_balance' in data:
                    data['full_balance'] = float(data['full_balance'])
                if 'port' in data:
                    data['port'] = int(data['port'])
                if 'is_active' in data:
                    data['is_active'] = data['is_active'] == 'on'
                else:
                    data['is_active'] = False

            # Set default platform type if not provided
            data['platform_type'] = data.get('platform_type', 'MT5')
            
            prop_firm = PropFirm(**data)
            prop_firm.set_available_balance_to_full_balance()
            db.session.add(prop_firm)
            db.session.commit()

            # Redirect to the prop firms list view if it's a form submission
            if not request.is_json:
                return redirect(url_for('prop_firms.view_prop_firms'))

            return jsonify({
                "status": "success",
                "prop_firm_id": prop_firm.id
            })
        except Exception as e:
            db.session.rollback()
            if request.is_json:
                return jsonify({
                    "status": "error",
                    "message": str(e)
                }), 400
            # Flash error message and redirect back to form if it's a form submission
            flash(f'Error creating prop firm: {str(e)}', 'error')
            return redirect(url_for('prop_firms.create_prop_firm_view'))


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


@bp.route('/view/create', methods=['GET'])
def create_prop_firm_view():
    form = PropFirmForm()
    return render_template('prop_firms/create_prop_firm.html', form=form)


@bp.route('/<int:prop_firm_id>/edit', methods=['GET'])
def edit_prop_firm(prop_firm_id):
    prop_firm = db.session.get(PropFirm, prop_firm_id)
    if not prop_firm:
        flash('Prop Firm not found', 'error')
        return redirect(url_for('prop_firms.view_prop_firms'))
    
    form = PropFirmForm(obj=prop_firm)
    return render_template('prop_firms/edit_prop_firm.html', form=form, prop_firm=prop_firm)

@bp.route('/<int:prop_firm_id>', methods=['PUT'])
def update_prop_firm(prop_firm_id):
    # a for or a JSON object can be received
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
        db_prop_firm.is_active = 1 if received_data.get('is_active') == 'y' else 0
        
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


@bp.route('/<int:prop_firm_id>/trade_pairs', methods=['GET', 'POST'])
def manage_trade_pairs(prop_firm_id):
    prop_firm = db.session.get(PropFirm, prop_firm_id)
    if not prop_firm:
        flash('Prop Firm not found', 'error')
        return redirect(url_for('prop_firms.view_prop_firms'))
    
    if request.method == 'GET':
        # Get all trade pairs and mark the ones associated with this prop firm
        trade_pairs = TradePairs.query.all()
        current_associations = PropFirmTradePairAssociation.query.filter_by(prop_firm_id=prop_firm_id).all()
        
        # Create a dict of current associations for easy lookup
        current_assoc_dict = {assoc.trade_pair_id: assoc.label for assoc in current_associations}
        
        # Enhance trade pairs with association info
        for pair in trade_pairs:
            pair.is_associated = pair.id in current_assoc_dict
            pair.current_label = current_assoc_dict.get(pair.id, '')
        
        return render_template('prop_firms/manage_trade_pairs.html', 
                             prop_firm=prop_firm, 
                             trade_pairs=trade_pairs)
    
    elif request.method == 'POST':
        try:
            data = request.get_json()
            associations = data.get('associations', [])
            
            # Remove all existing associations
            PropFirmTradePairAssociation.query.filter_by(prop_firm_id=prop_firm_id).delete()
            
            # Add new associations
            for assoc in associations:
                new_assoc = PropFirmTradePairAssociation(
                    prop_firm_id=prop_firm_id,
                    trade_pair_id=assoc['trade_pair_id'],
                    label=assoc['label']
                )
                db.session.add(new_assoc)
            
            db.session.commit()
            return jsonify({"status": "success"})
            
        except Exception as e:
            db.session.rollback()
            return jsonify({
                "status": "error",
                "message": str(e)
            }), 400
