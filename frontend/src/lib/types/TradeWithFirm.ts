export type TradeWithFirm = {
    id: number;
    strategy: string;
    order_type: string;
    contracts: number;
    ticker: string;
    position_size: number;
    created_at: string;
    prop_firm: {
        id: number;
        name: string;
        available_balance: number;
        drawdown_percentage: number;
    };
};