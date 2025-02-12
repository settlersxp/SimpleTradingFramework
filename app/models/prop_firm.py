from app import db
from datetime import datetime
from app.models.trade import Trade
import importlib
from typing import Optional, ClassVar
from app.trade_actions.trade_interface import TradingInterface
import logging


class PropFirm(db.Model):
    __tablename__ = 'prop_firms'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    full_balance = db.Column(db.Float, nullable=False)
    available_balance = db.Column(db.Float, nullable=False)
    dowdown_percentage = db.Column(db.Float, nullable=False)
    is_active = db.Column(db.Boolean, nullable=False, default=False)
    username = db.Column(db.String(100), nullable=True)
    password = db.Column(db.String(100), nullable=True)
    ip_address = db.Column(db.String(100), nullable=True)
    port = db.Column(db.Integer, nullable=True)
    platform_type = db.Column(db.String(100), nullable=True)

    # One to many relationship with trades in a different association table
    trades = db.relationship('Trade', secondary='prop_firm_trades', backref='prop_firm', lazy=True)

    _trading_instance: ClassVar[Optional[TradingInterface]] = None
    
    @property
    def trading(self) -> Optional[TradingInterface]:
        """Get or create trading instance based on platform_type"""
        if not self._trading_instance and self.platform_type:
            try:
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
                if all([self.username, self.password, self.ip_address, self.port]):
                    self._trading_instance.connect({
                        'username': self.username,
                        'password': self.password,
                        'server': f"{self.ip_address}:{self.port}"
                    })
            except Exception as e:
                logging.error(f"Error creating trading instance: {e}")
                return None
                
        return self._trading_instance

    # when a prop firm is created, the available balance should be set to the full balance
    def set_available_balance_to_full_balance(self):
        self.available_balance = self.full_balance
        self.update_dowdown_percentage()

    # When a trade is added, the prop firm's available balance should be updated
    def update_available_balance(self, trade: Trade):
        self.available_balance -= abs(trade.position_size)
        self.update_dowdown_percentage()

    # When a trade is deleted, the prop firm's available balance should be updated
    def update_available_balance_on_delete(self, trade: Trade):
        self.available_balance += abs(trade.position_size)
        self.update_dowdown_percentage()
    
    # every time the prop firm's available balance is updated, the downdraft percentage should be updated
    def update_dowdown_percentage(self):
        self.dowdown_percentage = self.full_balance/self.available_balance

    # When the full balance is update the downdraft percentage should be updated
    def update_dowdown_percentage_on_full_balance_update(self, full_balance: float):
        self.full_balance = full_balance
        self.update_dowdown_percentage()

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'created_at': self.created_at.isoformat(),
            'full_balance': self.full_balance,
            'available_balance': self.available_balance,
            'dowdown_percentage': self.dowdown_percentage,
            'is_active': self.is_active,
            'username': self.username,
            'password': self.password,
            'ip_address': self.ip_address,
            'port': self.port,
            'platform_type': self.platform_type
        }

    def to_insert_dict(self):
        # only the fields that are not nullable should be included
        to_return = {}
        for name, value in self.__dict__.items():
            # if value is a function, skip it
            if callable(value):
                continue

            if name.startswith('_'):
                continue
            
            if name == 'id':
                continue

            if value is not None:
                to_return[name] = value
        return to_return
