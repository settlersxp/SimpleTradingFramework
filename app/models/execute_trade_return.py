import json

class ExecuteTradeReturn:
    def __init__(self,
        success: bool,
        message: str,
        trade_id: int,
        details: dict,
        queued: bool = False):        
        """
        Initialize the ExecuteTradeReturn object
        """
        self.success = success
        self.message = message
        self.trade_id = trade_id
        self.details = details
        self.queued = queued

    def to_dict(self):
        return {
            'success': self.success,
            'message': self.message,
            'trade_id': self.trade_id,
            'details': self.details
        }

    def to_string(self):
        return json.dumps(self.to_dict())
