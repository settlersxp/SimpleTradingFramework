from app import db
from datetime import datetime
import json

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
