import MetaTrader5 as mt5
from typing import Dict, Any
from .trade_interface import TradingInterface
import logging
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.models.trade import Trade

logger = logging.getLogger(__name__)

class MT5Trading(TradingInterface):
    def __init__(self):
        self.connected = False
        self.mt_path = "G:\\MetaTrader 5\\terminal64.exe"
        
    def connect(self, credentials: Dict[str, Any]) -> bool:
        """
        Connect to MT5 terminal
        
        Args:
            credentials (dict): {
                'username': str,
                'password': str,
                'server': str,
                'path': str (optional)
            }
        """
        try:
            # Initialize MT5
            if not mt5.initialize(
                login=credentials.get('username'),
                password=credentials.get('password'),
                server=credentials.get('server'),
                path=self.mt_path
            ):
                logger.error(f"MT5 initialization failed: {mt5.last_error()}")
                return False
            
            self.connected = True
            logger.info("Successfully connected to MT5")
            return True
            
        except Exception as e:
            logger.error(f"Error connecting to MT5: {e}")
            self.connected = False
            return False
    
    def place_trade(self, trade: 'Trade') -> Dict[str, Any]:
        """
        Place trade on MT5
        
        Args:
            trade_details (dict): {
                'symbol': str,
                'volume': float,
                'type': str ('BUY' or 'SELL'),
                'price': float (optional),
                'stop_loss': float (optional),
                'take_profit': float (optional),
                'comment': str (optional)
            }
        """
        if not self.connected:
            # try to reconnect and in case of failure return the error
            if not self.connect(self.credentials):
                return {
                    'success': False,
                    'message': 'Not connected to MT5',
                    'trade_id': None,
                    'details': {}
                }
        
        try:
            # Prepare trade request
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": trade.symbol,
                "volume": float(trade.volume),
                "type": mt5.ORDER_TYPE_BUY if trade.type.upper() == 'BUY' else mt5.ORDER_TYPE_SELL,
                "price": trade.price,
                "deviation": 20,
                "magic": 234000,
                "comment": trade.comment,
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }
            
            # Add optional parameters if provided
            if trade.get('stop_loss'):
                request["sl"] = float(trade['stop_loss'])
            if trade.get('take_profit'):
                request["tp"] = float(trade['take_profit'])
            
            # Send trade request
            result = mt5.order_send(request)
            
            if result.retcode != mt5.TRADE_RETCODE_DONE:
                return {
                    'success': False,
                    'message': f"Order failed: {result.comment}",
                    'trade_id': None,
                    'details': {
                        'retcode': result.retcode,
                        'comment': result.comment
                    }
                }
            
            return {
                'success': True,
                'message': 'Trade placed successfully',
                'trade_id': str(result.order),
                'details': {
                    'volume': result.volume,
                    'price': result.price,
                    'request_id': result.request_id
                }
            }
            
        except Exception as e:
            logger.error(f"Error placing trade: {e}")
            return {
                'success': False,
                'message': f"Error placing trade: {str(e)}",
                'trade_id': None,
                'details': {}
            } 