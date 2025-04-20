from app import db


class PropFirmTrades(db.Model):
    """Helper class for managing trade associations."""

    __tablename__ = "prop_firm_trades"

    prop_firm_id = db.Column(
        db.Integer, db.ForeignKey("prop_firms.id"), primary_key=True
    )
    trade_id = db.Column(db.Integer, db.ForeignKey("trades.id"), primary_key=True)
    platform_id = db.Column(db.Integer, nullable=True)
    response = db.Column(db.JSON, nullable=True)  # New column for MT5 trade ID

    # Define relationships to both sides
    prop_firm = db.relationship("PropFirm", back_populates="trade_associations")
    trade = db.relationship("Trade", back_populates="prop_firm_associations")

    def __init__(self, prop_firm_id, trade_id, platform_id=None, response=None):
        """Initialize a PropFirmTrades instance."""
        self.prop_firm_id = prop_firm_id
        self.trade_id = trade_id
        self.platform_id = platform_id
        self.response = response

    @staticmethod
    def associate_trade_with_prop_firms(trade):
        """
        Associates a trade with all existing prop firms.

        Args:
            trade: The trade object to associate with prop firms.

        Returns:
            The trade object and the association.
        """
        from app.models.prop_firm import PropFirm

        prop_firms = PropFirm.query.all()
        for prop_firm in prop_firms:
            # Create a new association instance
            association = PropFirmTrades(prop_firm_id=prop_firm.id, trade_id=trade.id)
            db.session.add(association)
            prop_firm.update_available_balance(trade)

        db.session.commit()
        return trade, association

    @staticmethod
    def associate_trade(
        trade,
        prop_firm,
        platform_id,
        response,
    ):
        """
        Associates a trade with a prop firm.
        """
        association = PropFirmTrades(
            prop_firm_id=prop_firm.id,
            trade_id=trade.id,
            platform_id=platform_id,
            response=response,
        )
        db.session.add(association)
        db.session.commit()
        return association

    def to_dict(self):
        """
        Convert the PropFirmTrades model to a dictionary
        """
        return {
            "prop_firm_id": self.prop_firm_id,
            "trade_id": self.trade_id,
            "platform_id": self.platform_id,
            "response": self.response,
        }
