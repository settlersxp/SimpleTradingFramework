import { fail } from "@sveltejs/kit";
import type { Actions, PageServerLoad } from "./$types";
import type { TradingStrategy } from "$lib/types/TradingStrategy";

export const load: PageServerLoad = async ({ fetch, locals }) => {
    // Assuming user ID is available in locals
    const userId = locals.user?.id;

    if (!userId) {
        // Handle case where user is not authenticated or ID is missing
        // This might involve redirecting or throwing an error
        // For now, we'll return empty arrays, but a real app should handle this robustly
        console.error("User ID not found in locals");
        return {
            allStrategies: [] as TradingStrategy[],
            userStrategies: [] as TradingStrategy[],
            error: "User not found",
        };
    }

    try {
        // Fetch all strategies and user's strategies in parallel
        const [allStrategiesResponse, userStrategiesResponse] = await Promise.all([
            fetch("/api/trading_strategies"),
            fetch(`/api/trading_strategies/user/${userId}`),
        ]);

        if (!allStrategiesResponse.ok) {
            console.error(
                `Failed to fetch all strategies: ${allStrategiesResponse.statusText}`,
            );
            // Consider returning a specific error state
        }
        if (!userStrategiesResponse.ok) {
            console.error(
                `Failed to fetch user strategies: ${userStrategiesResponse.statusText}`,
            );
            // Consider returning a specific error state
        }

        const allStrategies = allStrategiesResponse.ok
            ? await allStrategiesResponse.json()
            : [];
        const userStrategies = userStrategiesResponse.ok
            ? await userStrategiesResponse.json()
            : [];

        return {
            allStrategies: allStrategies as TradingStrategy[],
            userStrategies: userStrategies as TradingStrategy[],
        };
    } catch (error) {
        console.error("Error loading trading strategies:", error);
        // Return error state to the page
        return {
            allStrategies: [] as TradingStrategy[],
            userStrategies: [] as TradingStrategy[],
            error: "Failed to load trading strategies.",
        };
    }
};

export const actions: Actions = {
    default: async ({ request, fetch, locals }) => {
        const userId = locals.user?.id;
        if (!userId) {
            return fail(401, { error: "User not authenticated" });
        }

        const formData = await request.formData();
        // Get all selected strategy IDs. If none are selected, getAll returns null.
        const selectedIds = formData.getAll("strategy_ids")?.map(Number) || [];

        try {
            const response = await fetch(
                `/api/trading_strategies/user/${userId}`,
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify({
                        strategy_ids: selectedIds,
                        clear_existing: true, // Keep the same logic as before
                    }),
                },
            );

            if (!response.ok) {
                let errorMessage = "Failed to save trading strategies";
                try {
                    const errorData = await response.json();
                    errorMessage = errorData.error || errorMessage;
                } catch (e) {
                    // Ignore error if response body is not JSON
                }
                return fail(response.status, { error: errorMessage });
            }

            // Optionally return success message or redirect
            return { success: "Trading strategies updated successfully" };
        } catch (err) {
            console.error("Error saving user strategies:", err);
            let message = "An unknown error occurred while saving.";
            if (err instanceof Error) {
                message = err.message;
            }
            return fail(500, { error: message });
        }
    },
};
