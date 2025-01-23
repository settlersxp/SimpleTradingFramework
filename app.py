from flask import Flask, jsonify, request, render_template
from flask_migrate import Migrate
from config import DevelopmentConfig, Config
from models import db, Trade, PropFirm, prop_firm_trades

app = Flask(__name__)
app.config.from_object(DevelopmentConfig)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = Config.SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = Config.SQLALCHEMY_TRACK_MODIFICATIONS

# Initialize database and migrations
db.init_app(app)
migrate = Migrate(app, db)

# Create tables
with app.app_context():
    db.create_all()

def add_trade_associations(mt_string):
    trade = Trade.from_mt_string(mt_string)
    db.session.add(trade)
    db.session.commit()

    # Add trade to all prop firms
    prop_firms = db.session.query(PropFirm).all()
    for prop_firm in prop_firms:
        prop_firm.trades.append(trade)
        prop_firm.update_available_balance(trade)    
    db.session.commit()
    return trade


@app.route('/', methods=['GET'])
def hello():
    return jsonify({"message": "Hello, World!"})


@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy"})


@app.route('/trades/<int:trade_id>', methods=['GET'])
def get_trade(trade_id):
    trade = db.session.get(Trade, trade_id)
    if not trade:
        return jsonify({"error": "Trade not found"}), 404
    return jsonify(trade.to_dict())

@app.route('/trades', methods=['GET', 'POST'])
def trades():
    if request.method == 'GET':
        trades = db.session.query(Trade).all()
        return jsonify({
            "trades": [trade.to_dict() for trade in trades]
        })
    elif request.method == 'POST':
        mt_string = request.get_data(as_text=True)
        trade = add_trade_associations(mt_string)
        return jsonify({
            "status": "success",
            "trade_id": trade.id
        })

@app.route('/trades_associations', methods=['GET', 'POST', 'PUT'])
def trades_associations():
    if request.method == 'GET':
        # Query trades through prop_firm_trades association table
        trades_with_firms = db.session.query(Trade, PropFirm)\
            .select_from(Trade)\
            .join(prop_firm_trades, Trade.id == prop_firm_trades.c.trade_id)\
            .join(PropFirm, PropFirm.id == prop_firm_trades.c.prop_firm_id)\
            .order_by(Trade.created_at.desc())\
            .all()

        # Format the response to include both trade and prop firm info
        return jsonify([{
                **trade.to_dict(),
                "prop_firm": {
                    "id": prop_firm.id,
                    "name": prop_firm.name
                }
            } for trade, prop_firm in trades_with_firms])
    elif request.method == 'POST':
        try:
            mt_string = request.get_data(as_text=True)
            trade = add_trade_associations(mt_string)
            return jsonify({
                "status": "success",
                "trade_id": trade.id
            })
        except Exception as e:
            db.session.rollback()  # Rollback on error
            return jsonify({
                "status": "error",
                "message": str(e)
            }), 400
    elif request.method == 'PUT':
        try:
            data = request.get_json()
            
            # Extract data from request
            strategy = data.get('strategy')
            order_type = data.get('order')  # Note: 'order' in request maps to 'order_type' in model
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



@app.route('/prop_firms', methods=['GET', 'POST'])
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
        prop_firm = PropFirm(**data)
        prop_firm.set_available_balance_to_full_balance()
        db.session.add(prop_firm)
        db.session.commit()
        return jsonify({
            "status": "success",
            "prop_firm_id": prop_firm.id
        })
    


@app.route('/prop_firms/<int:prop_firm_id>', methods=['DELETE', 'GET'])
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


@app.route('/prop_firm/<int:prop_firm_id>/trades', methods=['GET'])
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


@app.route('/view/trades')
def view_trades():
    trades_with_firms = db.session.query(Trade, PropFirm)\
        .select_from(Trade)\
        .join(prop_firm_trades, Trade.id == prop_firm_trades.c.trade_id)\
        .join(PropFirm, PropFirm.id == prop_firm_trades.c.prop_firm_id)\
        .order_by(Trade.created_at.desc())\
        .all()
    return render_template('trades.html', trades_with_firms=trades_with_firms)

@app.route('/view/prop_firms')
def view_prop_firms():
    prop_firms = PropFirm.query.all()
    return render_template('prop_firms.html', prop_firms=prop_firms)

@app.route('/view/prop_firms/<int:prop_firm_id>/edit')
def edit_prop_firm(prop_firm_id):
    prop_firm = db.session.get(PropFirm, prop_firm_id)
    if not prop_firm:
        return "Prop Firm not found", 404
    return render_template('edit_prop_firm.html', prop_firm=prop_firm)

@app.route('/prop_firms/<int:prop_firm_id>', methods=['PUT'])
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3200)
