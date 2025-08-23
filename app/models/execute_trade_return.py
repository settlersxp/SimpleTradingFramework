"""Structured message returned after a trade has been attempted"""

import json
from typing import Optional, Union


class ExecuteTradeReturn:
    def __init__(
        self,
        success: bool,
        message: str,
        trade_id: Optional[Union[int, str]],
        details: dict,
        queued: bool = False,
    ):
        """
        Initialize the ExecuteTradeReturn object.

        Args:
            success (bool): Indicates if the trade execution was successful.
            message (str): A message providing additional information about
                          the trade execution.
            trade_id (Optional[Union[int, str]]): The ID of the trade that
                                                 was executed.
            details (dict): A dictionary containing details about the
                           trade execution.
            queued (bool): Indicates if the trade is queued (default is False).
        """
        self.success = success
        self.message = message
        self.trade_id = trade_id
        self.details = details
        self.queued = queued

    def to_dict(self):
        """Convert the ExecuteTradeReturn object to a dictionary.

        Returns:
            dict: A dictionary representation of the ExecuteTradeReturn object.
        """
        return {
            "success": self.success,
            "message": self.message,
            "trade_id": self.trade_id,
            "details": self.details,
        }

    def to_string(self):
        """Convert the ExecuteTradeReturn object to a JSON string.

        Returns:
            str: A JSON string representation of the ExecuteTradeReturn object.
        """
        return json.dumps(self.to_dict())
