from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Association table for the many-to-many relationship between PropFirm and Trade
prop_firm_trades = db.Table('prop_firm_trades',
    db.Column('prop_firm_id', db.Integer, db.ForeignKey('prop_firms.id'), primary_key=True),
    db.Column('trade_id', db.Integer, db.ForeignKey('trades.id'), primary_key=True)
)

class Trade(db.Model):
    __tablename__ = 'trades'
    
    id = db.Column(db.Integer, primary_key=True)
    strategy = db.Column(db.String(100), nullable=False)
    order_type = db.Column(db.String(10), nullable=False)
    contracts = db.Column(db.Float, nullable=False)
    ticker = db.Column(db.String(20), nullable=False)
    position_size = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'strategy': self.strategy,
            'order_type': self.order_type,
            'contracts': self.contracts,
            'ticker': self.ticker,
            'position_size': self.position_size,
            'created_at': self.created_at.isoformat()
        }

    @staticmethod
    def from_mt_string(mt_string: str):
        # Convert the string to a proper dictionary format
        mt_string = '{' + mt_string + '}'
        # Replace single quotes with double quotes if needed
        mt_string = mt_string.replace("'", '"')
        
        import json
        try:
            data = json.loads(mt_string)
            return Trade(
                strategy=data['strategy'],
                order_type=data['order'],
                contracts=float(data['contracts']),
                ticker=data['ticker'],
                position_size=float(data['position_size'])
            )
        except (json.JSONDecodeError, KeyError) as e:
            raise ValueError(f"Invalid MT string format: {e}") 

    @staticmethod
    def update_matching_trades(strategy, order_type, contracts, ticker, position_size):
        """Update all trades that match the given criteria"""
        matching_trades = Trade.query.filter_by(
            strategy=strategy,
            order_type=order_type,
            ticker=ticker,
            position_size=position_size
        ).all()

        for trade in matching_trades:
            # if the future dowdown_percentage is greater than 4% skip the trade
            for prop_firm in trade.prop_firm:
                prop_firm.update_available_balance(trade)
                if prop_firm.dowdown_percentage > 1.04:
                    continue

                trade.contracts = contracts
                trade.position_size = position_size

        db.session.commit()
        return matching_trades

class PropFirm(db.Model):
    __tablename__ = 'prop_firms'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    full_balance = db.Column(db.Float, nullable=False)
    available_balance = db.Column(db.Float, nullable=False)
    dowdown_percentage = db.Column(db.Float, nullable=False)
    is_active = db.Column(db.Boolean, nullable=False, default=False)
    username = db.Column(db.String(100), nullable=True)
    password = db.Column(db.String(100), nullable=True)
    ip_address = db.Column(db.String(100), nullable=True)
    port = db.Column(db.Integer, nullable=True)
    platform_type = db.Column(db.String(100), nullable=True)

    # One to many relationship with trades in a different association table
    trades = db.relationship('Trade', secondary='prop_firm_trades', backref='prop_firm', lazy=True)

    # when a prop firm is created, the available balance should be set to the full balance
    def set_available_balance_to_full_balance(self):
        self.available_balance = self.full_balance
        self.update_dowdown_percentage()

    # When a trade is added, the prop firm's available balance should be updated
    def update_available_balance(self, trade: Trade):
        self.available_balance -= abs(trade.position_size)
        self.update_dowdown_percentage()

    # When a trade is deleted, the prop firm's available balance should be updated
    def update_available_balance_on_delete(self, trade: Trade):
        self.available_balance += abs(trade.position_size)
        self.update_dowdown_percentage()
    
    # every time the prop firm's available balance is updated, the downdraft percentage should be updated
    def update_dowdown_percentage(self):
        self.dowdown_percentage = self.full_balance/self.available_balance

    # When the full balance is update the downdraft percentage should be updated
    def update_dowdown_percentage_on_full_balance_update(self, full_balance: float):
        self.full_balance = full_balance
        self.update_dowdown_percentage()

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'created_at': self.created_at.isoformat(),
            'full_balance': self.full_balance,
            'available_balance': self.available_balance,
            'dowdown_percentage': self.dowdown_percentage,
            'is_active': self.is_active,
            'username': self.username,
            'password': self.password,
            'ip_address': self.ip_address,
            'port': self.port,
            'platform_type': self.platform_type
        }

    def to_insert_dict(self):
        # only the fields that are not nullable should be included
        to_return = {}
        for name, value in self.__dict__.items():
            # if value is a function, skip it
            if callable(value):
                continue

            if name.startswith('_'):
                continue
            
            if name == 'id':
                continue

            if value is not None:
                to_return[name] = value
        return to_return