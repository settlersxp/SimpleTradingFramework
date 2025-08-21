import MetaTrader5 as mt5
from typing import Dict, Any, List, Tuple
from .trade_interface import TradingInterface
import logging
from datetime import datetime
from threading import Timer, Lock
from typing import TYPE_CHECKING
from app.models.execute_trade_return import ExecuteTradeReturn
from app.models.signal import Signal
from app.models.trade import Trade
from app import db

if TYPE_CHECKING:
    from app.models.prop_firm import PropFirm
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
        # Check if MT5 is already running
        account_info = mt5.account_info()
        if account_info:
            same_user = int(account_info.login) == int(credentials.get("username"))
            if same_user:
                self.connected = True
                return True
            else:
                mt5.shutdown()
                self.connected = False

        try:
            # Initialize MT5
            if not mt5.initialize(
                login=int(credentials.get("username")),
                password=credentials.get("password"),
                server=credentials.get("server"),
                path=self.mt_path,
            ):
                logger.error("MT5 initialization failed: %s", mt5.last_error())
                return False
            self.connected = True
            logger.info("Successfully connected to MT5")
            return True
        except Exception as e:
            logger.error("Error connecting to MT5: %s", e)
            self.connected = False
            return False

    def close_trade(self, trade: Trade) -> ExecuteTradeReturn:
        """
        Cancel a trade on MT5
        """
        try:
            self.connect(self.credentials)

            existing_trades = mt5.positions_get()
            result = mt5.Close(
                symbol=trade.ticker,
                ticket=trade.platform_id,
            )

            if not result:
                import json

                print("Will retry with SL and TP")
                # Set take profit and stop loss at 5% of current value for both buy and sell
                # Note: This code sets SL/TP after closing, which may not be the intended behavior
                # Typically SL/TP would be set when opening or modifying existing positions
                try:
                    # Get symbol information for current price
                    symbol_info = mt5.symbol_info(trade.ticker)
                    tick = mt5.symbol_info_tick(trade.ticker)
                    order_type = existing_trades[0].type
                    # Determine current price based on order type
                    if order_type == mt5.ORDER_TYPE_BUY:
                        current_price = tick.ask
                        # For buy orders: SL below current price, TP above
                        stop_loss = current_price * 0.98  # 2% below
                        take_profit = current_price * 1.02  # 2% above
                    else:  # SELL order
                        current_price = tick.bid
                        # For sell orders: SL above current price, TP below
                        stop_loss = current_price * 1.02  # 2% above
                        take_profit = current_price * 0.98  # 2% below
                    
                    # Round to appropriate decimal places based on symbol digits
                    digits = symbol_info.digits
                    stop_loss = round(stop_loss, digits)
                    take_profit = round(take_profit, digits)
                    
                    logger.info(
                        f"Calculated SL/TP for {trade.ticker}: SL={stop_loss}, TP={take_profit}"
                    )
                except Exception as sl_tp_error:
                    logger.error(f"Error calculating SL/TP for {trade.ticker}: {sl_tp_error}")
                    # Continue with trade closure even if SL/TP calculation fails

                try:
                    request = {
                        "action": mt5.TRADE_ACTION_SLTP,
                        "position": trade.platform_id,
                        "sl": stop_loss,
                        "tp": take_profit,
                    }
                    result = mt5.order_send(request)
                except Exception as e:
                    logger.error(f"Error sending SL/TP for {trade.ticker}: {e}")
                    # Continue with trade closure even if SL/TP modification fails

                print(result)
                print(mt5.last_error())

            if not result:
                error_message = (
                    f"Error canceling trade: {trade.ticker} {trade.platform_id}"
                )
                print(result)
                return ExecuteTradeReturn(
                    success=False,
                    message=error_message,
                    trade_id=trade.platform_id,
                    details={},
                )

            remaining_trades = mt5.positions_get()
            if len(remaining_trades) != len(existing_trades) - 1:
                return ExecuteTradeReturn(
                    success=False,
                    message="Trade failed to be canceled even if the broker returned a success code",
                    trade_id=trade.platform_id,
                    details={},
                )

            success_message = (
                f"Trade canceled successfully {trade.ticker} {trade.platform_id}"
            )
            print(success_message)
            return ExecuteTradeReturn(
                success=True,
                message=success_message,
                trade_id=trade.platform_id,
                details={"retcode": result, "result": result},
            )
        except Exception as e:
            logger.error("Error canceling trade: %s", e)
            return ExecuteTradeReturn(
                success=False,
                message=f"Tried to close trade but failed with error: {str(e)}",
                trade_id=trade.platform_id,
                details={"result": mt5.last_error()},
            )

    def place_trade(self, trade: "Signal", label: str) -> ExecuteTradeReturn:
        """
        Place trade on MT5 with queue system

        Args:
            trade: Trade object
            label: label of the trade
        """
        # Check if we need to queue this trade
        current_time = datetime.now()

        with self.queue_lock:
            if self.last_trade_time is not None and (
                (current_time - self.last_trade_time).total_seconds()
                < self.cooldown_period
            ):
                # Add to queue if we're in cooldown period
                logger.info("Trade for %s added to queue (cooldown active)", label)
                self.trade_queue.append((trade, label, current_time))

                # Start the queue processor if not already running
                if (
                    self.processing_timer is None
                    or not self.processing_timer.is_alive()
                ):
                    remaining_cooldown = (
                        self.cooldown_period
                        - (current_time - self.last_trade_time).total_seconds()
                    )
                    self.processing_timer = Timer(
                        remaining_cooldown, self._process_trade_queue
                    )
                    self.processing_timer.daemon = True
                    self.processing_timer.start()

                return ExecuteTradeReturn(
                    success=True,
                    message="Trade queued for later execution",
                    trade_id=None,
                    details={},
                    queued=True,
                )
            else:
                logger.info("Executing trade immediately")
                # If not in cooldown, execute the trade immediately
                result = self._execute_trade(trade, label)

            if result.success:
                self.last_trade_time = datetime.now()

            return result

    def _process_trade_queue(self):
        """Process queued trades after cooldown period"""
        with self.queue_lock:
            if not self.trade_queue:
                self.processing_timer = None
                return

            # Process the oldest trade in the queue
            trade, label, queue_time = self.trade_queue.pop(0)
            logger.info(
                "Processing queued trade for %s (queued at %s)",
                label,
                queue_time,
            )

            # Execute the trade with updated prices
            result = self._execute_trade(trade, label)

            if result.success:
                self.last_trade_time = datetime.now()

            # If there are more trades in the queue,
            # schedule the next processing
            if self.trade_queue:
                self.processing_timer = Timer(
                    self.cooldown_period, self._process_trade_queue
                )
                self.processing_timer.daemon = True
                self.processing_timer.start()
            else:
                self.processing_timer = None

    def _execute_trade(self, trade: "Signal", label: str) -> ExecuteTradeReturn:
        """Execute a trade with MT5"""
        self.connect(self.credentials)

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
                    details={},
                )

            # Make sure the symbol is selected in Market Watch
            if not symbol_info.visible:
                if not mt5.symbol_select(label, True):
                    return ExecuteTradeReturn(
                        success=False,
                        message=f"Failed to select {label} in Market Watch",
                        trade_id=None,
                        details={},
                    )

            # Get current price data - always get fresh data for queued trades
            tick = mt5.symbol_info_tick(label)
            if tick is None:
                return ExecuteTradeReturn(
                    success=False,
                    message=f"No price data available for {label}",
                    trade_id=None,
                    details={},
                )

            # Determine price based on order type
            price = tick.ask if trade.order_type.upper() == "BUY" else tick.bid

            order_type = (
                mt5.ORDER_TYPE_BUY
                if trade.order_type.upper() == "BUY"
                else mt5.ORDER_TYPE_SELL
            )

            existing_trades = mt5.positions_get()

            request, result = self.try_to_place_order(trade, label, price, order_type)

            number_of_tries = 0
            while (
                trade.contracts > 0.01
                and result.retcode != mt5.TRADE_RETCODE_DONE
                and number_of_tries < 10
            ):

                # lower the contract size by 20%
                trade.contracts = round(trade.contracts * 0.8, 2)

                # Try to place the order
                request, result = self.try_to_place_order(
                    trade, label, price, order_type
                )

                number_of_tries += 1

            # Add optional parameters if provided
            # if tra`de.get('stop_loss'):
            #     request["sl"] = float(trade['stop_loss'])
            # if trade.get('take_profit'):
            #     request["tp"] = float(trade['take_profit'])
            # Send trade request

            if result.retcode == mt5.TRADE_RETCODE_MARKET_CLOSED:
                return ExecuteTradeReturn(
                    success=False,
                    message="Market is closed",
                    trade_id=None,
                    details={
                        "retcode": result.retcode,
                        "comment": result.comment,
                    },
                )
            elif not result or result.retcode != mt5.TRADE_RETCODE_DONE:
                return ExecuteTradeReturn(
                    success=False,
                    message=f"Order failed: {result.comment}",
                    trade_id=None,
                    details={
                        "retcode": result.retcode,
                        "comment": result.comment,
                    },
                )

            new_trades = mt5.positions_get()
            if len(new_trades) != len(existing_trades) + 1:
                return ExecuteTradeReturn(
                    success=False,
                    message="Trade failed to be placed even if the broker returned a success code",
                    trade_id=None,
                    details={},
                )

            # From the new trades filter the one that is not in the existing trades
            placed_trade = [
                trade for trade in new_trades if trade not in existing_trades
            ][0]

            # Return the trade details upon successful placement
            return ExecuteTradeReturn(
                success=True,
                message="Trade placed successfully",
                trade_id=str(result.order),
                details={
                    "volume": result.volume,
                    "price": result.price,
                    "request_id": result.request_id,
                    "buy_request": request,
                    "response": placed_trade,
                },
            )
        except Exception as e:
            logger.error("Error placing trade: %s", e)
            logger.error(trade.to_string())
            return ExecuteTradeReturn(
                success=False,
                message=f"Error placing trade: {str(e)}",
                trade_id=None,
                details={},
            )

    def try_to_place_order(self, trade, label, price, order_type):
        good_return_codes = [
            mt5.TRADE_RETCODE_PLACED,
            mt5.TRADE_RETCODE_DONE,
            mt5.TRADE_RETCODE_DONE_PARTIAL,
        ]

        bad_return_codes = [
            mt5.TRADE_RETCODE_INVALID_FILL,
            mt5.TRADE_RETCODE_PRICE_OFF,
            mt5.TRADE_RETCODE_MARKET_CLOSED,
        ]

        # If the filling type failed, try another one
        list_of_filling_types = [
            mt5.ORDER_FILLING_BOC,
            mt5.ORDER_FILLING_FOK,
            mt5.ORDER_FILLING_IOC,
            mt5.ORDER_FILLING_RETURN,
        ]

        for filling_type in list_of_filling_types:
            # Prepare trade request
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": label,
                "volume": trade.contracts,
                "type": order_type,
                "price": price,
                "deviation": max(int(trade.position_size), 20),
                "magic": 234000,
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": filling_type,
            }
            result = mt5.order_send(request)

            # if rejected, try another filling type
            if result.retcode == mt5.TRADE_RETCODE_INVALID_FILL:
                continue

            # The broker does not offer a price for
            # this type of order, market is closed or invalid fill
            if result.retcode in bad_return_codes:
                break

            # Placed successfully
            if result.retcode in good_return_codes:
                break

        return request, result

    def is_connected(self) -> bool:
        self.connect(self.credentials)
        account_info = mt5.account_info()
        return account_info is not None

    def _find_best_matching_strategy(self, symbol: str, prop_firm: "PropFirm") -> str:
        """
        Find the best matching trading strategy for a symbol based on character similarity.
        
        Args:
            symbol: The trading symbol (e.g., "EURUSD", "BTCUSD")
            prop_firm: The prop firm to get strategies for (unused, kept for compatibility)
            
        Returns:
            The name of the best matching strategy or "NO_STRATEGY" if no good match found
        """
        from app.models.trading_strategy import TradingStrategy
        
        # Get all trading strategies from the database
        all_strategies = TradingStrategy.query.all()
        
        if not all_strategies:
            return "NO_STRATEGY"
        
        # Find the strategy with the most matching characters
        best_match = None
        best_score = 0
        
        symbol_lower = symbol.lower()
        
        for strategy in all_strategies:
            strategy_lower = strategy.name.lower()
            
            # Count common characters between symbol and strategy name
            common_chars = 0
            for char in symbol_lower:
                if char in strategy_lower:
                    common_chars += 1
            
            # Calculate a score based on common characters relative to symbol length
            score = common_chars / len(symbol_lower) if len(symbol_lower) > 0 else 0
            
            if score > best_score:
                best_score = score
                best_match = strategy.name
        
        # Only return a match if we have some reasonable similarity (at least 20% of characters match)
        if best_score >= 0.2 and best_match:
            return best_match
        
        return "NO_STRATEGY"

    def sync_prop_firm(
        self, prop_firm: "PropFirm"
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Synchronize prop firm information with MT5.
        Updates account information and creates new trades.
        """
        to_return = {}

        self.connect(self.credentials)

        # Get account information
        account_info = mt5.account_info()
        if not account_info:
            raise Exception("Failed to get account information for %s" % prop_firm.name)

        to_return = dict(account_info._asdict())
        # Calculate drawdown percentage
        if account_info.balance > 0:
            to_return["drawdown_percentage"] = (
                (account_info.balance - account_info.equity) / account_info.balance
            ) * 100

        prop_firm.update_available_balance(account_info.margin_free)
        prop_firm.name = account_info.company
        prop_firm.save()

        to_return["trades"] = []
        # Get open positions
        positions = mt5.positions_get()

        for position in positions:
            # Check if trade already exists
            existing_trade = Trade.query.filter_by(
                platform_id=str(position.ticket),
                prop_firm_id=prop_firm.id,
            ).first()

            if not existing_trade:
                # Find the best matching strategy for this symbol
                strategy_name = self._find_best_matching_strategy(position.symbol, prop_firm)
                
                new_signal = Signal(
                    strategy=strategy_name,
                    order_type="buy" if position.type == mt5.ORDER_TYPE_BUY else "sell",
                    contracts=position.volume,
                    ticker=position.symbol,
                    position_size=abs(position.profit + position.swap),
                )
                new_signal = Signal.create_new_signal(new_signal)

                existing_trade = Trade.associate_signal(
                    new_signal,
                    prop_firm,
                    str(position.ticket),
                    position._asdict(),
                    position.symbol,
                )

            # join with the signal table to get the strategy name
            new_signal = Signal.query.filter_by(id=existing_trade.signal_id).first()
            output_trade = existing_trade.to_dict()
            output_trade["strategy"] = new_signal.strategy
            output_trade["order_type"] = new_signal.order_type
            output_trade["contracts"] = new_signal.contracts
            output_trade["ticker"] = new_signal.ticker
            output_trade["position_size"] = new_signal.position_size

            to_return["trades"].append(output_trade)

        # Remove from trade to prop firm association table the trades
        # that don't exist in positions for the current prop firm
        trades_to_delete = Trade.query.filter(
            Trade.prop_firm_id == prop_firm.id,
            Trade.platform_id.notin_([str(position.ticket) for position in positions]),
        ).all()
        for trade in trades_to_delete:
            db.session.delete(trade)

        # If there are no trades in MT5 delete all the trades for the current prop firm
        if not positions:
            Trade.query.filter(
                Trade.prop_firm_id == prop_firm.id,
            ).delete()

        db.session.commit()

        return to_return
