from app import db

class PropFirmTradePairAssociation(db.Model):
    __tablename__ = 'prop_firm_trade_pair_association'
    
    prop_firm_id = db.Column(db.Integer, db.ForeignKey('prop_firms.id'), primary_key=True)
    label = db.Column(db.String(100), nullable=False)
    trade_pair_id = db.Column(db.Integer, db.ForeignKey('trade_pairs.id'), primary_key=True)

