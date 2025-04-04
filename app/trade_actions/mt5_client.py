import MetaTrader5 as mt5
from typing import Dict, List, Optional, Any
import time
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

class MT5Client:
    def __init__(self, username: str, password: str, server: str, port: int):
        self.username = username
        self.password = password
        self.server = server
        self.port = port
        self._mt5_initialized = False

    def connect(self) -> bool:
        """Initialize and connect to MT5 terminal."""
        try:
            # Initialize MT5 if not already initialized
            if not self._mt5_initialized:
                if not mt5.initialize():
                    logger.error(f"MT5 initialization failed: {mt5.last_error()}")
                    return False
                self._mt5_initialized = True

            # Connect to the account
            if not mt5.login(
                login=int(self.username),
                password=self.password,
                server=f"{self.server}:{self.port}"
            ):
                logger.error(f"MT5 login failed: {mt5.last_error()}")
                return False

            return True
        except Exception as e:
            logger.error(f"Error connecting to MT5: {str(e)}")
            return False

    def disconnect(self):
        """Shutdown MT5 connection."""
        if self._mt5_initialized:
            mt5.shutdown()
            self._mt5_initialized = False

    def get_account_info(self) -> Optional[Dict[str, Any]]:
        """Get account information from MT5."""
        try:
            if not self._ensure_connection():
                return None

            account_info = mt5.account_info()
            if account_info is None:
                logger.error("Failed to get account info")
                return None

            return {
                'balance': float(account_info.balance),
                'equity': float(account_info.equity),
                'margin': float(account_info.margin),
                'free_margin': float(account_info.margin_free),
                'margin_level': float(account_info.margin_level) if account_info.margin_level is not None else 0.0,
                'leverage': int(account_info.leverage),
                'currency': account_info.currency,
                'server': account_info.server,
                'trade_mode': account_info.trade_mode,
            }
        except Exception as e:
            logger.error(f"Error getting account info: {str(e)}")
            return None

    def get_open_positions(self) -> Optional[List[Dict[str, Any]]]:
        """Get all open positions from MT5."""
        try:
            if not self._ensure_connection():
                return None

            positions = mt5.positions_get()
            if positions is None:
                logger.error(f"No positions found: {mt5.last_error()}")
                return []

            return [{
                'ticket': position.ticket,
                'symbol': position.symbol,
                'volume': float(position.volume),
                'type': 'buy' if position.type == mt5.POSITION_TYPE_BUY else 'sell',
                'price_open': float(position.price_open),
                'price_current': float(position.price_current),
                'profit': float(position.profit),
                'swap': float(position.swap),
                'time': datetime.fromtimestamp(position.time, tz=timezone.utc).isoformat(),
                'magic': position.magic,
                'comment': position.comment,
            } for position in positions]
        except Exception as e:
            logger.error(f"Error getting open positions: {str(e)}")
            return None

    def _ensure_connection(self) -> bool:
        """Ensure MT5 is connected, attempt reconnection if needed."""
        if not mt5.terminal_info():
            logger.info("MT5 not connected, attempting to reconnect...")
            return self.connect()
        return True

    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect() 