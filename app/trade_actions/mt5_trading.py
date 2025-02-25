import MetaTrader5 as mt5
from typing import Dict, Any
from .trade_interface import TradingInterface
import logging
from datetime import datetime
from threading import Timer, Lock
from typing import TYPE_CHECKING
from app.models.execute_trade_return import ExecuteTradeReturn
if TYPE_CHECKING:
    from app.models.trade import Trade

logger = logging.getLogger(__name__)


class MT5Trading(TradingInterface):
    def __init__(self):
        self.credentials = None
        self.connected = False
        self.mt_path = "G:\\MetaTrader 5\\terminal64.exe"
        self.trade_queue = []  # Queue to store pending trades
        self.last_trade_time = None  # Timestamp of the last executed trade
        self.cooldown_period = 60  # Cooldown period in seconds (1 minute)
        self.queue_lock = Lock()  # Lock for thread-safe queue operations
        self.processing_timer = None  # Timer for processing the queue

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
        mt5.shutdown()
        try:
            # Initialize MT5
            if not mt5.initialize(
                login=int(credentials.get('username')),
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

    def cancel_trade(self, old_trade: 'Trade') -> ExecuteTradeReturn:
        """
        Cancel a trade on MT5
        """
        try:
            result = mt5.order_send(old_trade.response)
            if result.retcode != mt5.TRADE_RETCODE_DONE:
                return ExecuteTradeReturn(
                    success=False,
                    message=f"Error canceling trade: {result.comment}",
                    trade_id=None,
                    details={}
                )
            return ExecuteTradeReturn(
                success=True,
                message='Trade canceled successfully',
                trade_id=None,
                details={
                    'retcode': result.retcode,
                    'result': result
                }
            )
        except Exception as e:
            logger.error(f"Error canceling trade: {e}")
            return ExecuteTradeReturn(
                success=False,
                message=f"Error canceling trade: {str(e)}"
            )

    def place_trade(self, trade: 'Trade', label: str) -> ExecuteTradeReturn:
        """
        Place trade on MT5 with queue system

        Args:
            trade: Trade object
            label: label of the trade
        """
        # Check if we need to queue this trade
        current_time = datetime.now()

        with self.queue_lock:
            if (self.last_trade_time is not None and
                    (current_time - self.last_trade_time).total_seconds() < self.cooldown_period):
                # Add to queue if we're in cooldown period
                logger.info(
                    f"Trade for {label} added to queue (cooldown active)")
                self.trade_queue.append((trade, label, current_time))

                # Start the queue processor if not already running
                if self.processing_timer is None or not self.processing_timer.is_alive():
                    remaining_cooldown = self.cooldown_period - \
                        (current_time - self.last_trade_time).total_seconds()
                    self.processing_timer = Timer(
                        remaining_cooldown, self._process_trade_queue)
                    self.processing_timer.daemon = True
                    self.processing_timer.start()

                return ExecuteTradeReturn(
                    success=True,
                    message='Trade queued for later execution',
                    trade_id=None,
                    details={},
                    queued=True
                )

            # If not in cooldown, execute the trade immediately
            result = self._execute_trade(trade, label)

            if result.success:
                self.last_trade_time = current_time

            return result

    def _process_trade_queue(self):
        """Process queued trades after cooldown period"""
        with self.queue_lock:
            if not self.trade_queue:
                self.processing_timer = None
                return

            current_time = datetime.now()

            # Process the oldest trade in the queue
            trade, label, queue_time = self.trade_queue.pop(0)
            logger.info(
                f"Processing queued trade for {label} (queued at {queue_time})")

            # Execute the trade with updated prices
            result = self._execute_trade(trade, label)

            if result['success']:
                self.last_trade_time = current_time

            # If there are more trades in the queue, schedule the next processing
            if self.trade_queue:
                self.processing_timer = Timer(
                    self.cooldown_period, self._process_trade_queue)
                self.processing_timer.daemon = True
                self.processing_timer.start()
            else:
                self.processing_timer = None

    def _execute_trade(self, trade: 'Trade', label: str) -> ExecuteTradeReturn:
        """Execute a trade with MT5"""
        if not self.connected:
            # try to reconnect and in case of failure return the error
            self.connected = False
            return self.connect(self.credentials)

        try:
            # Check if symbol exists and has valid price data
            symbol_info = mt5.symbol_info(label)
            if symbol_info is None:
                return ExecuteTradeReturn(
                    success=False,
                    message=f"Symbol {label} not found",
                    trade_id=None,
                    details={}
                )

            # Make sure the symbol is selected in Market Watch
            if not symbol_info.visible:
                if not mt5.symbol_select(label, True):
                    return ExecuteTradeReturn(
                        success=False,
                        message=f"Failed to select {label} in Market Watch",
                        trade_id=None,
                        details={}
                    )

            # Get current price data - always get fresh data for queued trades
            tick = mt5.symbol_info_tick(label)
            if tick is None:
                return ExecuteTradeReturn(
                    success=False,
                    message=f"No price data available for {label}",
                    trade_id=None,
                    details={}
                )

            # Determine price based on order type
            price = tick.ask if trade.order_type.upper() == 'BUY' else tick.bid

            order_type = mt5.ORDER_TYPE_BUY if trade.order_type.upper(
            ) == 'BUY' else mt5.ORDER_TYPE_SELL

            # Prepare trade request
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": label,
                "volume": max(trade.contracts, 0.1),
                "type": order_type,
                "price": price,
                "deviation": max(int(trade.position_size), 20),
                "magic": 234000,
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_BOC
            }

            # Add optional parameters if provided
            # if trade.get('stop_loss'):
            #     request["sl"] = float(trade['stop_loss'])
            # if trade.get('take_profit'):
            #     request["tp"] = float(trade['take_profit'])
            # Send trade request
            result = mt5.order_send(request)
            if result.retcode == mt5.TRADE_RETCODE_MARKET_CLOSED:
                return ExecuteTradeReturn(
                    success=False,
                    message='Market is closed',
                    trade_id=None,
                    details={
                        'retcode': result.retcode,
                        'comment': result.comment
                    }
                )
            elif not result or result.retcode != mt5.TRADE_RETCODE_DONE:
                return ExecuteTradeReturn(
                    success=False,
                    message=f"Order failed: {result.comment}",
                    trade_id=None,
                    details={
                        'retcode': result.retcode,
                        'comment': result.comment
                    }
                )
            # Return the trade details upon successful placement
            return ExecuteTradeReturn(
                success=True,
                message='Trade placed successfully',
                trade_id=str(result.order),
                details={
                    'volume': result.volume,
                    'price': result.price,
                    'request_id': result.request_id,
                    'buy_request': request,
                    'response': result
                }
            )
        except Exception as e:
            logger.error(f"Error placing trade: {e}")
            logger.error(trade.to_string())
            return ExecuteTradeReturn(
                success=False,
                message=f"Error placing trade: {str(e)}",
                trade_id=None,
                details={}
            )

    def is_connected(self) -> bool:
        self.connect(self.credentials)
        account_info = mt5.account_info()
        return account_info is not None
