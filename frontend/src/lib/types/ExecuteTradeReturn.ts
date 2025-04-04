export interface ExecuteTradeReturn {
    success: boolean;
    message: string;
    trade_id: number | null;
    details: {
        volume?: number;
        price?: number;
        request_id?: number;
        buy_request?: any; // MT5 specific request object
        response?: any; // MT5 specific response object
        [key: string]: any; // Allow for additional details
    };
    queued?: boolean;
} 