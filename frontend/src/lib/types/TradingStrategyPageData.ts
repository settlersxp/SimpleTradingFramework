import type { TradingStrategy } from "./TradingStrategy";

// Define the expected shape of the data returned by the load function
export type TradingStrategiesPageData = {
    strategies: TradingStrategy[];
    loading: boolean;
    error: string | null;
};