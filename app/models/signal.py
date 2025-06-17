from app import db, TimezoneAwareModel
from datetime import datetime, timezone
import json
import re


class Signal(TimezoneAwareModel):
    """
    Signal model
    """

    __tablename__ = "signals"

    id = db.Column(db.Integer, primary_key=True)
    strategy = db.Column(db.String(100), nullable=False)
    order_type = db.Column(db.String(10), nullable=False)
    contracts = db.Column(db.Float, nullable=False)
    ticker = db.Column(db.String(20), nullable=False)
    position_size = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))

    # Define the relationship with Trade
    prop_firm_associations = db.relationship(
        "Trade",
        back_populates="signal",
    )

    # Define a relationship to access prop firms directly
    prop_firms = db.relationship(
        "PropFirm",
        secondary="trades",
        viewonly=True,
    )

    def to_dict(self):
        """
        Convert the Trade model to a dictionary
        """
        return {
            "id": self.id,
            "strategy": self.strategy,
            "order_type": self.order_type,
            "contracts": self.contracts,
            "ticker": self.ticker,
            "position_size": self.position_size,
            "created_at": self.get_datetime_in_timezone(self.created_at).strftime(
                "%Y-%m-%d %H:%M:%S %z"
            ),
        }

    def to_string(self):
        """
        Convert the Trade model to a string
        """
        return json.dumps(self.to_dict())

    @staticmethod
    def create_new_signal(new_signal):
        """
        Create a new signal
        """
        db.session.add(new_signal)
        db.session.commit()
        return new_signal

    @staticmethod
    def from_mt_string(mt_string: str):
        """
        Convert a MT string to a Trade model.

        There are two formats for the MT string:
        "\"strategy\":\"Stiff Zone\", \"order\":\"sell\", \"contracts\":\"0.001\", \"ticker\":\"BTCUSDT.P\", \"position_size\":\"-0.001\""
        '"strategy":"Stiff Zone", "order":"sell", "contracts":"0.001", "ticker":"BTCUSDT.P", "position_size":-0.001'
        """
        try:
            # Handle both escaped and unescaped formats
            if mt_string.startswith('"'):
                # Handle escaped format by unescaping
                mt_string = mt_string.encode().decode("unicode_escape")
                mt_string = mt_string.strip('"')
            else:
                # Handle unescaped format by stripping outer quotes
                mt_string = mt_string.strip("'")

            # Format as proper JSON
            formatted_string = "{" + mt_string.strip() + "}"

            # Try to parse the JSON
            try:
                data = json.loads(formatted_string)
            except json.JSONDecodeError:
                # Apply regex to fix unquoted values if needed
                formatted_string = re.sub(
                    r'(?<="ticker":)([^\s",]+)', r'"\1"', formatted_string
                )
                data = json.loads(formatted_string)

            # Create a Signal instance using the extracted data
            return Signal(
                strategy=data["strategy"],
                order_type=data["order"],
                contracts=float(data["contracts"]),
                ticker=data["ticker"],
                position_size=float(data["position_size"]),
            )

        except (json.JSONDecodeError, KeyError) as e:
            raise ValueError(f"Invalid MT string format: {e}")

    @staticmethod
    def update_matching_trades(
        strategy,
        order_type,
        contracts,
        ticker,
        position_size,
    ):
        """Update all trades that match the given criteria"""
        matching_trades = Signal.query.filter_by(
            strategy=strategy,
            order_type=order_type,
            ticker=ticker,
            position_size=position_size,
        ).all()

        for trade in matching_trades:
            # if the future drawdown_percentage is greater than 4% skip the trade
            for prop_firm in trade.prop_firms:
                prop_firm.update_available_balance(trade)
                if prop_firm.drawdown_percentage > 1.04:
                    continue

                trade.contracts = contracts
                trade.position_size = position_size

        db.session.commit()
        return matching_trades

    @staticmethod
    def get_signal_by_mt_string(mt_string: str):
        """
        Get a signal by its MT string
        """
        new_signal = Signal.from_mt_string(mt_string)
        existing_signal = Signal.query.filter_by(
            strategy=new_signal.strategy,
            order_type=new_signal.order_type,
            ticker=new_signal.ticker,
            position_size=new_signal.position_size,
        ).first()
        return existing_signal
