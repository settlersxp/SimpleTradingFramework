from app import db
from app.models.signal import Signal
from app.models.prop_firm import PropFirm


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
        db.String(50),
        nullable=True,
    )
    response = db.Column(
        db.JSON,
        nullable=True,
    )  # New column for MT5 signal ID

    # Define relationships to both sides
    prop_firm = db.relationship(
        "PropFirm",
        back_populates="trades",
    )
    signal = db.relationship(
        "Signal",
        back_populates="prop_firm_associations",
    )

    created_at = db.Column(
        db.DateTime,
        default=db.func.now(),
    )
    ticker = db.Column(
        db.String(10),
        nullable=True,
    )

    def __init__(
        self,
        prop_firm_id,
        signal_id,
        platform_id=None,
        response=None,
        ticker=None,
    ):
        """Initialize a Trades instance."""
        self.prop_firm_id = prop_firm_id
        self.signal_id = signal_id
        self.platform_id = platform_id
        self.response = response
        self.ticker = ticker

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
            prop_firm.update_available_balance_with_trade(signal)

        db.session.commit()
        return signal, association

    @staticmethod
    def associate_signal(
        signal: Signal,
        prop_firm: PropFirm,
        platform_id: str,
        response: dict,
        ticker: str,
    ):
        """
        Place a trade with this prop firm.
        """
        # Check if a trade already exists for this prop_firm / signal pair. The
        # composite primary-key (prop_firm_id, signal_id) must be unique, so
        # attempting to insert duplicates will raise an ``IntegrityError``.  If
        # a record already exists we simply update its details and return it.

        existing_trade: "Trade" | None = Trade.query.filter_by(
            prop_firm_id=prop_firm.id,
            signal_id=signal.id,
        ).first()

        if existing_trade:
            # Update the existing record with the latest execution details.
            existing_trade.platform_id = platform_id
            existing_trade.response = response
            existing_trade.ticker = ticker
            db.session.commit()
            return existing_trade

        # No previous record – create a brand-new association.
        new_trade = Trade(
            prop_firm_id=prop_firm.id,
            signal_id=signal.id,
            platform_id=platform_id,
            response=response,
            ticker=ticker,
        )
        db.session.add(new_trade)
        db.session.commit()
        return new_trade

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


# ---------------------------------------------------------------------------
# Compatibility shim --------------------------------------------------------
# ---------------------------------------------------------------------------

# Historically other modules imported ``associate_signal`` directly from
# ``app.models.trade``.  Provide a thin wrapper so these imports continue to
# work after refactoring.


def associate_signal(*args, **kwargs):  # noqa: D401
    """Compatibility wrapper for ``Trade.associate_signal``."""

    return Trade.associate_signal(*args, **kwargs)
