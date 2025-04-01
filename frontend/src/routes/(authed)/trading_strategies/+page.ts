import type { ServerLoad, ServerLoadEvent } from "@sveltejs/kit";
import type { TradingStrategy } from "$lib/types/TradingStrategy";
import type { TradingStrategiesPageData } from "$lib/types/TradingStrategyPageData";

// Load function to fetch initial strategies
export const load: ServerLoad = async ({ fetch }: ServerLoadEvent): Promise<TradingStrategiesPageData> => {
    try {
        const response = await fetch("/api/trading_strategies");
        if (!response.ok) {
            console.error("Failed to fetch trading strategies:", response.statusText);
            return {
                strategies: [],
                loading: false,
                error: `Failed to load strategies: ${response.statusText}`,
            };
        }
        const strategies: TradingStrategy[] = await response.json();
        return {
            strategies,
            loading: false,
            error: null,
        };
    } catch (err) {
        console.error("Error loading trading strategies:", err);
        return {
            strategies: [],
            loading: false,
            error: "An unexpected error occurred while loading strategies.",
        };
    }
};
