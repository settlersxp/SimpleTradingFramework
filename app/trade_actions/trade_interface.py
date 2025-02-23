from abc import ABC, abstractmethod
from typing import Dict, Any
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.trade import Trade

class TradingInterface(ABC):
    """Abstract base class for trading platform interactions"""

    @abstractmethod
    def connect(self, credentials: Dict[str, Any]) -> bool:
        """
        Connect to the trading platform

        Args:
            credentials (dict): Dictionary containing connection credentials
                              (username, password, server, etc.)

        Returns:
            bool: True if connection successful, False otherwise
        """
        pass

    @abstractmethod
    def place_trade(self, trade: 'Trade', label: str) -> Dict[str, Any]:
        """
        Place a trade on the platform

        Args:
            trade_details (dict): Dictionary containing trade details
                                (ticker, type, volume, etc.)
            label (str): Label for the trade symbol specific to the prop firm

        Returns:
            dict: Response containing trade status and details
                 {
                     'success': bool,
                     'trade_id': str,
                     'message': str,
                     'details': dict
                 }
        """
        pass

    @abstractmethod
    def is_connected(self) -> bool:
        """
        Check if the connection is active
        """
        pass
