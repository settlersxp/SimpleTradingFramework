import type { ExecuteTradeReturn } from './ExecuteTradeReturn';

export type Trade = {
    id: number;
    signal_id?: number;
    prop_firm_id?: number;
    platform_id?: number;
    strategy: string;
    order_type: string;
    contracts: number;
    ticker: string;
    position_size: number;
    created_at: string;
    response: ExecuteTradeReturn | null;
};