from flask import Blueprint, jsonify, request
from app.models.signal import Signal
from app import db

bp = Blueprint("signals", __name__)


@bp.route("/list", methods=["GET"])
def list_signals():
    signals = db.session.query(Signal).order_by(Signal.id.desc()).all()
    return jsonify({"signals": [signal.to_dict() for signal in signals]})


@bp.route("/create", methods=["POST"])
def create_signal():
    # save the signal to the database
    mt_string = request.get_data(as_text=True)
    return save_signal(mt_string)


@staticmethod
def save_signal(mt_string):
    signal = Signal.from_mt_string(mt_string)
    db.session.add(signal)
    db.session.commit()
    return signal.to_dict()
