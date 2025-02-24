from app import db
from datetime import datetime


class TradePairs(db.Model):
    """
    TradePair model
    """
    __tablename__ = 'trade_pairs'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        """
        Convert the TradePair model to a dictionary
        """
        return {
            'id': self.id,
            'name': self.name,
            'created_at': self.created_at.isoformat()
        }
