from app import db
from datetime import datetime

class TradePairs(db.Model):
    __tablename__ = 'trade_pairs'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

