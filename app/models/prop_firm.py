from app import db, TimezoneAwareModel
from datetime import datetime, timezone
from app.models.signal import Signal
from app.models.user import user_prop_firm
import importlib
import logging
from typing import Optional, List, TYPE_CHECKING
from sqlalchemy.orm import relationship
from app.trade_actions.trade_interface import TradingInterface

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.trade import Trade


class PropFirm(TimezoneAwareModel):
    __tablename__ = "prop_firms"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(
        db.DateTime,
        default=datetime.now(timezone.utc),
    )
    full_balance = db.Column(db.Float, nullable=False)
    available_balance = db.Column(db.Float, nullable=False)
    drawdown_percentage = db.Column(db.Float, nullable=False)
    is_active = db.Column(db.Boolean, nullable=False, default=False)
    username = db.Column(db.String(100), nullable=True)
    password = db.Column(db.String(100), nullable=True)
    ip_address = db.Column(db.String(100), nullable=True)
    port = db.Column(db.Integer, nullable=True)
    platform_type = db.Column(db.String(100), nullable=True)
    description = db.Column(db.String(500), nullable=True)

    # Direct relationships for easier access
    trades = relationship(
        "Trade",
        back_populates="prop_firm",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )

    # Many-to-many relationship with users
    users = relationship(
        "User",
        secondary=user_prop_firm,
        back_populates="prop_firms",
        lazy="dynamic",
    )

    # Note: _trading_instance is set dynamically in __init__
    # to avoid SQLAlchemy mapping

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._trading_instance: Optional[TradingInterface] = None

    def get_active_trades(self) -> List["Trade"]:
        """Get all active trades for this prop firm"""
        return self.trades.all()

    def get_users(self) -> List["User"]:
        """Get all users associated with this prop firm"""
        return list(self.users.all())

    def add_user(self, user) -> bool:
        """Add a user to this prop firm"""
        if user not in self.users:
            self.users.append(user)
            return True
        return False

    def remove_user(self, user) -> bool:
        """Remove a user from this prop firm"""
        if user in self.users:
            self.users.remove(user)
            return True
        return False

    @property
    def trading(self) -> Optional[TradingInterface]:
        """Get or create trading instance based on platform_type"""
        # Ensure _trading_instance exists (for existing database records)
        if not hasattr(self, "_trading_instance"):
            self._trading_instance = None

        if not self._trading_instance and self.platform_type:
            # Convert platform type to module name
            # (e.g., 'MT5' -> 'mt5_trading')
            module_name = f"{self.platform_type.lower()}_trading"
            # Import the module
            module = importlib.import_module(f"app.trade_actions.{module_name}")
            # Get the class
            # (assumes class name is platform type + 'Trading')
            class_name = f"{self.platform_type.upper()}Trading"
            trading_class = getattr(module, class_name)
            # Create instance
            self._trading_instance = trading_class(self)

            # Try to connect if we have credentials
            if self.has_complete_credentials():
                try:
                    if self._trading_instance:
                        self._trading_instance.connect()
                except Exception as e:
                    logger.error("Failed to connect trading instance: %s", e)

            # Credentials are now handled through the prop_firm reference

        return self._trading_instance

    def is_connected(self) -> bool:
        # Implement your logic to check if the connection is active
        # Ensure _trading_instance exists (for existing database records)
        if not hasattr(self, "_trading_instance"):
            self._trading_instance = None

        return (
            self._trading_instance is not None and self._trading_instance.is_connected()
        )

    # When a prop firm is created, the available balance should be
    # set to the full balance
    def set_available_balance_to_full_balance(self):
        self.available_balance = self.full_balance
        self.update_drawdown_percentage()

    # When a trade is added, the prop firm's available balance
    # should be updated
    def update_available_balance_with_trade(self, trade: Signal):
        self.available_balance -= abs(trade.position_size)
        self.update_drawdown_percentage()

    # When a trade is deleted, the prop firm's available balance
    # should be updated
    def update_available_balance_on_delete(self, trade: Signal):
        self.available_balance += abs(trade.position_size)
        self.update_drawdown_percentage()

    # Every time the prop firm's available balance is updated,
    # the drawdown percentage should be updated
    def update_drawdown_percentage(self):
        self.drawdown_percentage = self.full_balance / self.available_balance

    # When the full balance is updated the drawdown percentage
    # should be updated
    def update_drawdown_percentage_on_full_balance_update(self, full_balance: float):
        self.full_balance = full_balance
        self.update_drawdown_percentage()

    def update_available_balance(self, balance: float):
        self.available_balance = balance
        self.update_drawdown_percentage()

    def has_complete_credentials(self) -> bool:
        """Check if all required credentials are present"""
        return all([self.username, self.password, self.ip_address])

    def get_total_position_size(self) -> float:
        """Calculate total position size across all trades"""
        return sum(trade.signal.position_size for trade in self.trades if trade.signal)

    def get_trade_count(self) -> int:
        """Get count of active trades"""
        return self.trades.count()

    def save(self):
        db.session.add(self)
        db.session.commit()

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "created_at": (
                self.created_at.strftime("%Y-%m-%d %H:%M:%S %z")
                if self.created_at
                else None
            ),
            "full_balance": self.full_balance,
            "available_balance": self.available_balance,
            "drawdown_percentage": self.drawdown_percentage,
            "is_active": self.is_active,
            "username": self.username,
            "password": self.password,
            "ip_address": self.ip_address,
            "port": self.port,
            "platform_type": self.platform_type,
            "description": self.description,
        }

    def to_insert_dict(self):
        # only the fields that are not nullable should be included
        to_return = {}
        for name, value in self.__dict__.items():
            # if value is a function, skip it
            if callable(value):
                continue

            if name.startswith("_"):
                continue

            if name == "id":
                continue

            if value is not None:
                to_return[name] = value
        return to_return
