from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.execute_trade_return import ExecuteTradeReturn
    from app.models.signal import Signal
    from app.models.prop_firm import PropFirm
    from app.models.trade import Trade


class TradingInterface(ABC):
    """Abstract base class for trading platform interactions"""

    def __init__(self, prop_firm: Optional["PropFirm"] = None):
        """
        Initialize the trading interface with an optional PropFirm instance

        Args:
            prop_firm: PropFirm instance containing credentials and
                      configuration
        """
        self.prop_firm = prop_firm
        self._connected = False

    @property
    def credentials(self) -> Dict[str, Any]:
        """Get credentials from the associated PropFirm"""
        if self.prop_firm:
            return {
                "username": self.prop_firm.username,
                "password": self.prop_firm.password,
                "server": self.prop_firm.ip_address,
                "id": self.prop_firm.id,
            }
        return {}

    @abstractmethod
    def connect(self, credentials: Optional[Dict[str, Any]] = None) -> bool:
        """
        Connect to the trading platform

        Args:
            credentials (dict, optional): Dictionary containing connection
                                        credentials. If not provided, uses
                                        credentials from PropFirm

        Returns:
            bool: True if connection successful, False otherwise
        """
        pass

    @abstractmethod
    def place_trade(self, trade: "Signal", label: str) -> "ExecuteTradeReturn":
        """
        Place a trade on the platform

        Args:
            trade: Signal object containing trade details
            label (str): Label for the trade symbol specific to the prop firm

        Returns:
            ExecuteTradeReturn
        """
        pass

    @abstractmethod
    def close_trade(self, trade: "Trade") -> "ExecuteTradeReturn":
        """
        Close a trade on the platform

        Args:
            trade: Trade object to close

        Returns:
            ExecuteTradeReturn
        """
        pass

    @abstractmethod
    def is_connected(self) -> bool:
        """
        Check if the connection is active
        """
        pass
