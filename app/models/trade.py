from app import db


class Trade(db.Model):
    """Helper class for managing signal associations."""

    __tablename__ = "trades"

    prop_firm_id = db.Column(
        db.Integer,
        db.ForeignKey("prop_firms.id"),
        primary_key=True,
    )
    signal_id = db.Column(
        db.Integer,
        db.ForeignKey("signals.id"),
        primary_key=True,
    )
    platform_id = db.Column(
        db.Integer,
        nullable=True,
    )
    response = db.Column(
        db.JSON,
        nullable=True,
    )  # New column for MT5 signal ID

    # Define relationships to both sides
    prop_firm = db.relationship(
        "PropFirm",
        back_populates="trade_associations",
    )
    signal = db.relationship(
        "Signal",
        back_populates="prop_firm_associations",
    )

    created_at = db.Column(
        db.DateTime,
        default=db.func.now(),
    )

    def __init__(
        self,
        prop_firm_id,
        signal_id,
        platform_id=None,
        response=None,
    ):
        """Initialize a Trades instance."""
        self.prop_firm_id = prop_firm_id
        self.signal_id = signal_id
        self.platform_id = platform_id
        self.response = response

    @staticmethod
    def place_trade_with_prop_firms(signal):
        """
        Associates a signal with all existing prop firms.

        Args:
            signal: The signal object to place a trade with.

        Returns:
            The signal object and the association.
        """
        from app.models.prop_firm import PropFirm

        prop_firms = PropFirm.query.all()
        for prop_firm in prop_firms:
            # Create a new association instance
            association = Trade(
                prop_firm_id=prop_firm.id,
                signal_id=signal.id,
            )
            db.session.add(association)
            prop_firm.update_available_balance(signal)

        db.session.commit()
        return signal, association

    @staticmethod
    def associate_signal(
        signal,
        prop_firm,
        platform_id,
        response,
    ):
        """
        Place a trade with this prop firm.
        """
        trade = Trade(
            prop_firm_id=prop_firm.id,
            signal_id=signal.id,
            platform_id=platform_id,
            response=response,
        )
        db.session.add(trade)
        db.session.commit()
        return trade

    def to_dict(self):
        """
        Convert the Trades model to a dictionary
        """
        return {
            "prop_firm_id": self.prop_firm_id,
            "signal_id": self.signal_id,
            "platform_id": self.platform_id,
            "response": self.response,
            "created_at": self.created_at,
        }
