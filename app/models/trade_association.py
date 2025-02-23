from app import db


# Association table for the many-to-many relationship
# between PropFirm and Trade
prop_firm_trades = db.Table(
    'prop_firm_trades',
    db.Column(
        'prop_firm_id',
        db.Integer,
        db.ForeignKey('prop_firms.id'),
        primary_key=True),
    db.Column(
        'trade_id',
        db.Integer,
        db.ForeignKey('trades.id'),
        primary_key=True),
    db.Column('platform_id', db.Integer, nullable=True),
    db.Column('response', db.JSON, nullable=True)  # New column for MT5 trade ID
)


class TradeAssociation:
    """
    Helper class for managing trade associations
    """
    @staticmethod
    def associate_trade_with_prop_firms(trade):
        """
        Associates a trade with all existing prop firms
        """
        from app.models.prop_firm import PropFirm  # Import here to avoid circular imports
        
        prop_firms = PropFirm.query.all()
        for prop_firm in prop_firms:
            prop_firm.trades.append(trade)
            prop_firm.update_available_balance(trade)
        
        db.session.commit()
        return trade
