import type { Trade } from "./Trade";
import type { TradePair } from "./TradePairs";

export interface PropFirm {
    id: number;
    name: string;
    // Making these nullable based on Python model and common usage
    username?: string | null;
    ip_address?: string | null;
    port?: number | null;
    platform_type?: string | null;
    is_active: boolean;
    full_balance: number;
    available_balance: number;
    dowdown_percentage: number;
    created_at: string; // ISO format string expected from backend
    // updated_at is not explicitly in the Python to_dict, but was in original TS
    updated_at?: string;
    trades?: Trade[]; // Added from Python GET / response structure
    tradePairs?: TradePair[];
}

// Data for creating/updating a prop firm (Matches Python POST/PUT)
export interface PropFirmData {
    name: string;
    full_balance: number;
    available_balance?: number; // Optional, backend might default
    dowdown_percentage?: number; // Optional, backend might calculate
    is_active?: boolean;
    username?: string;
    password?: string;
    ip_address?: string;
    port?: number;
    platform_type?: string;
}

// Response for GET /user/prop_firms
export interface UserPropFirmsResponse {
    prop_firms?: PropFirm[];
    message?: string; // Added for consistency, though backend might not send
    error?: string;
}

// Response for GET /<id>/trades
export interface PropFirmTradesResponse {
    prop_firm: PropFirm;
    trades: Trade[]; // Replace 'any' with a specific Trade type if defined
    error?: string; // Keep error field for potential backend errors
}

// Trade pair info for GET /<id>/trade_pairs
export interface TradePairInfo {
    id: number;
    name: string;
    is_associated: boolean;
    current_label: string;
}

// Response for GET /<id>/trade_pairs
export interface PropFirmTradePairsResponse {
    prop_firm: PropFirm;
    trade_pairs: TradePairInfo[];
    error?: string; // Keep error field for potential backend errors
}

// Data for POST /<id>/trade_pairs
export interface TradePairAssociationUpdate {
    trade_pair_id: number;
    label: string;
}

// Generic API response types for better error handling
export interface SuccessResponse {
    status?: 'success'; // Status might not always be present
    message: string;
    // Include specific data fields based on the function's success response
    prop_firm?: PropFirm;
    prop_firms?: PropFirm[];
}

export interface ErrorResponse {
    status?: 'error';
    message?: string; // May be added by frontend catch
    error: string; // Main error message from backend or fetch
}
