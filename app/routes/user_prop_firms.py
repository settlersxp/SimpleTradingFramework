from flask import Blueprint, jsonify, session
from app import db
from app.models.user import User
from app.models.prop_firm import PropFirm
from app.routes.auth import login_required

user_prop_firms_bp = Blueprint('user_prop_firms', __name__)

@user_prop_firms_bp.route('/user/prop_firms', methods=['GET'])
@login_required
def get_user_prop_firms(user):
    prop_firms = [pf.to_dict() for pf in user.prop_firms]
    return jsonify({'prop_firms': prop_firms}), 200

@user_prop_firms_bp.route('/user/prop_firms/<int:prop_firm_id>', methods=['POST'])
@login_required
def add_prop_firm_to_user(user, prop_firm_id):
    prop_firm = PropFirm.query.get(prop_firm_id)
    if not prop_firm:
        return jsonify({'error': 'Prop firm not found'}), 404
    
    if user.add_prop_firm(prop_firm):
        db.session.commit()
        return jsonify({'message': 'Prop firm added to user successfully'}), 200
    else:
        return jsonify({'message': 'Prop firm already associated with user'}), 200

@user_prop_firms_bp.route('/user/prop_firms/<int:prop_firm_id>', methods=['DELETE'])
@login_required
def remove_prop_firm_from_user(user, prop_firm_id):
    prop_firm = PropFirm.query.get(prop_firm_id)
    if not prop_firm:
        return jsonify({'error': 'Prop firm not found'}), 404
    
    if user.remove_prop_firm(prop_firm):
        db.session.commit()
        return jsonify({'message': 'Prop firm removed from user successfully'}), 200
    else:
        return jsonify({'message': 'Prop firm not associated with user'}), 404
