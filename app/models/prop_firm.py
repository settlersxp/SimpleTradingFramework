from app import db, TimezoneAwareModel
from datetime import datetime, timezone
from app.models.signal import Signal
from app.models.user import user_prop_firm
import importlib
from typing import Optional, ClassVar, List, TYPE_CHECKING
from app.trade_actions.trade_interface import TradingInterface
from sqlalchemy import select

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

    # One to many relationship with trades in a different association table
    trade_associations = db.relationship(
        "Trade",
        back_populates="prop_firm",
    )

    _trading_instance: ClassVar[Optional[TradingInterface]] = None

    def get_trade_associations(self) -> List["Trade"]:
        return self.trade_associations

    def get_users(self) -> List["User"]:
        """Manually get all users associated with this prop firm"""
        from app.models.user import User

        stmt = (
            select(User)
            .join(user_prop_firm)
            .where(user_prop_firm.c.prop_firm_id == self.id)
        )
        return db.session.execute(stmt).scalars().all()

    def add_user(self, user):
        """Manually add a user to this prop firm"""
        if not self.id:
            # Save the prop firm first if it doesn't have an ID
            db.session.add(self)
            db.session.flush()

        # Check if relationship already exists
        stmt = select(user_prop_firm).where(
            user_prop_firm.c.user_id == user.id,
            user_prop_firm.c.prop_firm_id == self.id,
        )
        exists = db.session.execute(stmt).first() is not None

        if not exists:
            # Create the association
            db.session.execute(
                user_prop_firm.insert().values(
                    user_id=user.id,
                    prop_firm_id=self.id,
                    created_at=datetime.now(timezone.utc),
                )
            )
            return True
        return False

    def remove_user(self, user):
        """Manually remove a user from this prop firm"""
        result = db.session.execute(
            user_prop_firm.delete().where(
                user_prop_firm.c.user_id == user.id,
                user_prop_firm.c.prop_firm_id == self.id,
            )
        )
        return result.rowcount > 0

    @property
    def trading(self) -> Optional[TradingInterface]:
        """Get or create trading instance based on platform_type"""
        if not self._trading_instance and self.platform_type:
            # Convert platform type to module name (e.g., 'MT5' -> 'mt5_trading')
            module_name = f"{self.platform_type.lower()}_trading"
            # Import the module
            module = importlib.import_module(f"app.trade_actions.{module_name}")
            # Get the class (assumes class name is platform type + 'Trading')
            class_name = f"{self.platform_type.upper()}Trading"
            trading_class = getattr(module, class_name)
            # Create instance
            self._trading_instance = trading_class()

            # Try to connect if we have credentials
            if all([self.username, self.password, self.ip_address]):
                self._trading_instance.connect(
                    {
                        "username": self.username,
                        "password": self.password,
                        "server": f"{self.ip_address}",
                    }
                )

            self._trading_instance.credentials = {
                "username": self.username,
                "password": self.password,
                "server": f"{self.ip_address}",
            }

        return self._trading_instance

    def is_connected(self) -> bool:
        # Implement your logic to check if the connection is active
        return (
            self._trading_instance is not None and self._trading_instance.is_connected()
        )

    # when a prop firm is created, the available balance should be set to the full balance
    def set_available_balance_to_full_balance(self):
        self.available_balance = self.full_balance
        self.update_drawdown_percentage()

    # When a trade is added, the prop firm's available balance should be updated
    def update_available_balance(self, trade: Signal):
        self.available_balance -= abs(trade.position_size)
        self.update_drawdown_percentage()

    # When a trade is deleted, the prop firm's available balance should be updated
    def update_available_balance_on_delete(self, trade: Signal):
        self.available_balance += abs(trade.position_size)
        self.update_drawdown_percentage()

    # every time the prop firm's available balance is updated, the downdraft percentage should be updated
    def update_drawdown_percentage(self):
        self.drawdown_percentage = self.full_balance / self.available_balance

    # When the full balance is update the downdraft percentage should be updated
    def update_drawdown_percentage_on_full_balance_update(self, full_balance: float):
        self.full_balance = full_balance
        self.update_drawdown_percentage()

    def update_available_balance(self, balance: float):
        self.available_balance = balance
        self.update_drawdown_percentage()

    def save(self):
        db.session.add(self)
        db.session.commit()

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "created_at": self.get_datetime_in_timezone(self.created_at).strftime(
                "%Y-%m-%d %H:%M:%S %z"
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
