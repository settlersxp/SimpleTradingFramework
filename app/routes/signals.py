from flask import Blueprint, jsonify, request
from app.models.signal import Signal
from app import db
from app.routes.auth import login_required

bp = Blueprint("signals", __name__)


@login_required
@bp.route("/list", methods=["GET"])
def list_signals():
    signals = db.session.query(Signal).order_by(Signal.id.desc()).all()
    return jsonify({"signals": [signal.to_dict() for signal in signals]})


@login_required
@bp.route("/create", methods=["POST"])
def create_signal():
    # save the signal to the database
    mt_string = request.get_data(as_text=True)
    return save_signal(mt_string)


@login_required
@bp.route("/<int:signal_id>", methods=["DELETE"])
def delete_signal(signal_id):
    signal = db.session.get(Signal, signal_id)
    # if the signal is not found, return a 404 error
    if not signal:
        return jsonify({"message": "Signal not found"}), 404

    # if the signal is associated with a trade, don't delete it
    if signal.prop_firm_associations:
        return jsonify({"message": "Signal is associated with a trade"}), 400

    db.session.delete(signal)
    db.session.commit()
    return jsonify({"message": "Signal deleted successfully"})


@staticmethod
def save_signal(mt_string):
    signal = Signal.from_mt_string(mt_string)
    db.session.add(signal)
    db.session.commit()
    return signal.to_dict()
