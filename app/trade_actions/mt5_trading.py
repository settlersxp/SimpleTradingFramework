import MetaTrader5 as mt5
from typing import Dict, Any, Optional
from .trade_interface import TradingInterface
import logging
from datetime import datetime
from threading import Timer, Lock
from typing import TYPE_CHECKING
from app.models.execute_trade_return import ExecuteTradeReturn
from app.models.signal import Signal
from app.models.trade import Trade
from app.models.prop_firm_trade_pair_association import PropFirmTradePairAssociation
from app.models.trade_pairs import TradePairs
from app import db

if TYPE_CHECKING:
    from app.models.prop_firm import PropFirm

logger = logging.getLogger(__name__)


class MT5Trading(TradingInterface):
    def __init__(self, prop_firm: Optional["PropFirm"] = None):
        super().__init__(prop_firm)
        self.mt_path = None
        self.trade_queue = []  # Queue to store pending trades
        self.last_trade_time = None  # Timestamp of the last executed trade
        self.cooldown_period = 60  # Cooldown period in seconds (1 minute)
        self.queue_lock = Lock()  # Lock for thread-safe queue operations
        self.processing_timer = None  # Timer for processing the queue

    def set_mt_path(self, account_id: Optional[str] = None) -> str:
        """Set MT5 terminal path"""
        if account_id is None and self.prop_firm:
            account_id = str(self.prop_firm.id)

        self.mt_path = f"G:\\MetaTrader 5-{account_id}\\terminal64.exe"

        return self.mt_path

    def connect(self, credentials: Optional[Dict[str, Any]] = None) -> bool:
        """
        Connect to MT5 terminal

        Args:
            credentials (dict, optional): {
                'username': str,
                'password': str,
                'server': str,
                'id': str (optional)
            }
            If not provided, uses credentials from PropFirm
        """
        # Use provided credentials or get from PropFirm
        creds = credentials or self.credentials

        if not creds or not all(k in creds for k in ["username", "password", "server"]):
            logger.error("Missing required credentials")
            return False

        # Check if MT5 is already running
        account_info = mt5.account_info()
        if account_info:
            same_user = int(account_info.login) == int(creds.get("username", 0))
            if same_user:
                self._connected = True
                return True
            else:
                mt5.shutdown()
                self._connected = False

        try:
            # Initialize MT5
            if not mt5.initialize(
                login=int(creds.get("username", 0)),
                password=creds.get("password", ""),
                server=creds.get("server", ""),
                path=self.set_mt_path(creds.get("id")),
            ):
                logger.error("MT5 initialization failed: %s", mt5.last_error())
                return False
            self._connected = True
            logger.info("Successfully connected to MT5")
            return True
        except Exception as e:
            logger.error("Error connecting to MT5: %s", e)
            self._connected = False
            return False

    def close_trade(self, trade: Trade) -> ExecuteTradeReturn:
        """Cancel a trade on MT5"""
        try:
            if not self.connect():
                return ExecuteTradeReturn(
                    success=False,
                    message="Failed to connect to MT5",
                    trade_id=trade.platform_id,
                    details={},
                )

            existing_trades = mt5.positions_get()
            result = mt5.Close(
                symbol=trade.ticker,
                ticket=int(trade.platform_id) if trade.platform_id else 0,
            )

            if not result:
                logger.info("Will retry with SL and TP")
                # Set take profit and stop loss at 2% of current value
                try:
                    # Get symbol information for current price
                    symbol_info = mt5.symbol_info(trade.ticker)
                    tick = mt5.symbol_info_tick(trade.ticker)
                    if not existing_trades:
                        raise ValueError("No existing trades found")

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
                        "Calculated SL/TP for %s: SL=%s, TP=%s",
                        trade.ticker,
                        stop_loss,
                        take_profit,
                    )
                except Exception as sl_tp_error:
                    logger.error(
                        "Error calculating SL/TP for %s: %s", trade.ticker, sl_tp_error
                    )
                    stop_loss = None
                    take_profit = None

                if stop_loss is not None and take_profit is not None:
                    try:
                        request = {
                            "action": mt5.TRADE_ACTION_SLTP,
                            "position": (
                                int(trade.platform_id) if trade.platform_id else 0
                            ),
                            "sl": stop_loss,
                            "tp": take_profit,
                        }
                        result = mt5.order_send(request)
                    except Exception as e:
                        logger.error("Error sending SL/TP for %s: %s", trade.ticker, e)

                logger.debug("Result: %s", result)
                logger.debug("Last error: %s", mt5.last_error())

            if not result:
                error_message = (
                    f"Error canceling trade: {trade.ticker} " f"{trade.platform_id}"
                )
                logger.error(error_message)
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
                    message=(
                        "Trade failed to be canceled even if the broker "
                        "returned a success code"
                    ),
                    trade_id=trade.platform_id,
                    details={},
                )

            success_message = (
                f"Trade canceled successfully {trade.ticker} " f"{trade.platform_id}"
            )
            logger.info(success_message)
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
        """Place trade on MT5 with queue system"""
        current_time = datetime.now()

        with self.queue_lock:
            if self.last_trade_time is not None and (
                (current_time - self.last_trade_time).total_seconds()
                < self.cooldown_period
            ):
                logger.info("Trade for %s added to queue (cooldown active)", label)
                self.trade_queue.append((trade, label, current_time))

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

            trade, label, queue_time = self.trade_queue.pop(0)
            logger.info(
                "Processing queued trade for %s (queued at %s)",
                label,
                queue_time,
            )

            result = self._execute_trade(trade, label)

            if result.success:
                self.last_trade_time = datetime.now()

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
        if not self.connect():
            return ExecuteTradeReturn(
                success=False,
                message="Failed to connect to MT5",
                trade_id=None,
                details={},
            )

        try:
            symbol_info = mt5.symbol_info(label)
            if symbol_info is None:
                return ExecuteTradeReturn(
                    success=False,
                    message=f"Symbol {label} not found",
                    trade_id=None,
                    details={},
                )

            if not symbol_info.visible:
                if not mt5.symbol_select(label, True):
                    return ExecuteTradeReturn(
                        success=False,
                        message=f"Failed to select {label} in Market Watch",
                        trade_id=None,
                        details={},
                    )

            tick = mt5.symbol_info_tick(label)
            if tick is None:
                return ExecuteTradeReturn(
                    success=False,
                    message=f"No price data available for {label}",
                    trade_id=None,
                    details={},
                )

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
                trade.contracts = round(trade.contracts * 0.8, 2)
                request, result = self.try_to_place_order(
                    trade, label, price, order_type
                )
                number_of_tries += 1

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
                    message=(
                        "Trade failed to be placed even if the broker "
                        "returned a success code"
                    ),
                    trade_id=None,
                    details={},
                )

            placed_trade = [
                trade for trade in new_trades if trade not in existing_trades
            ][0]

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

        list_of_filling_types = [
            mt5.ORDER_FILLING_BOC,
            mt5.ORDER_FILLING_FOK,
            mt5.ORDER_FILLING_IOC,
            mt5.ORDER_FILLING_RETURN,
        ]

        request = None
        result = None

        for filling_type in list_of_filling_types:
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

            if result.retcode == mt5.TRADE_RETCODE_INVALID_FILL:
                continue

            if result.retcode in bad_return_codes:
                break

            if result.retcode in good_return_codes:
                break

        return request, result

    def is_connected(self) -> bool:
        if not self.connect():
            return False
        account_info = mt5.account_info()
        return account_info is not None

    def _find_best_matching_strategy(self, symbol: str, prop_firm: "PropFirm") -> str:
        """
        Find the best matching trading strategy for a symbol based on
        character similarity.
        """
        from app.models.trading_strategy import TradingStrategy

        all_strategies = TradingStrategy.query.all()

        if not all_strategies:
            return "NO_STRATEGY"

        best_match = None
        best_score = 0
        symbol_lower = symbol.lower()

        for strategy in all_strategies:
            strategy_lower = strategy.name.lower()
            common_chars = 0
            for char in symbol_lower:
                if char in strategy_lower:
                    common_chars += 1

            score = common_chars / len(symbol_lower) if len(symbol_lower) > 0 else 0

            if score > best_score:
                best_score = score
                best_match = strategy.name

        if best_score >= 0.2 and best_match:
            return best_match

        return "NO_STRATEGY"

    def sync_prop_firm(self, prop_firm: Optional["PropFirm"] = None) -> Dict[str, Any]:
        """Synchronize prop firm information with MT5."""
        target_prop_firm = prop_firm or self.prop_firm

        if not target_prop_firm:
            raise ValueError("No PropFirm instance available for synchronization")

        to_return = {}

        if not self.connect():
            raise Exception(f"Failed to connect to MT5 for {target_prop_firm.name}")

        account_info = mt5.account_info()
        if not account_info:
            raise Exception(
                f"Failed to get account information for {target_prop_firm.name}"
            )

        to_return = dict(account_info._asdict())
        if account_info.balance > 0:
            to_return["drawdown_percentage"] = (
                (account_info.balance - account_info.equity) / account_info.balance
            ) * 100

        target_prop_firm.update_available_balance(account_info.margin_free)
        target_prop_firm.name = account_info.company
        target_prop_firm.save()

        to_return["trades"] = []
        positions = mt5.positions_get()

        for position in positions:
            existing_trade = Trade.query.filter_by(
                platform_id=str(position.ticket),
                prop_firm_id=target_prop_firm.id,
            ).first()

            if not existing_trade:
                strategy_name = self._find_best_matching_strategy(
                    position.symbol, target_prop_firm
                )

                # Get the pop_firm_trade_pair_association for the prop_firm
                prop_firm_trade_pair_association = PropFirmTradePairAssociation.query.filter_by(
                    prop_firm_id=target_prop_firm.id,
                    label=position.symbol,
                ).first()

                if not prop_firm_trade_pair_association:
                    continue

                trade_pair = TradePairs.query.filter_by(
                    id=prop_firm_trade_pair_association.trade_pair_id,
                ).first()

                if not trade_pair:
                    logger.error(f"Trade pair not found for {position.symbol}")
                    continue

                new_signal = Signal(
                    strategy=strategy_name,
                    order_type=(
                        "buy" if position.type == mt5.ORDER_TYPE_BUY else "sell"
                    ),
                    contracts=position.volume,
                    ticker=trade_pair.name,
                    position_size=abs(position.profit + position.swap),
                )
                new_signal = Signal.create_new_signal(new_signal)

                existing_trade = Trade.associate_signal(
                    new_signal,
                    target_prop_firm,
                    str(position.ticket),
                    position._asdict(),
                    position.symbol,
                )

            new_signal = Signal.query.filter_by(id=existing_trade.signal_id).first()
            output_trade = existing_trade.to_dict()
            if new_signal:
                output_trade["strategy"] = new_signal.strategy
                output_trade["order_type"] = new_signal.order_type
                output_trade["contracts"] = new_signal.contracts
                output_trade["ticker"] = new_signal.ticker
                output_trade["position_size"] = new_signal.position_size

            to_return["trades"].append(output_trade)

        trades_to_delete = Trade.query.filter(
            Trade.prop_firm_id == target_prop_firm.id,
            Trade.platform_id.notin_([str(position.ticket) for position in positions]),
        ).all()
        for trade in trades_to_delete:
            db.session.delete(trade)

        if not positions:
            Trade.query.filter(
                Trade.prop_firm_id == target_prop_firm.id,
            ).delete()

        db.session.commit()
        return to_return
