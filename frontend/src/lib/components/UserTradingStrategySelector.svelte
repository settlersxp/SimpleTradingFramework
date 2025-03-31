<script lang="ts">
    import { onMount } from "svelte";
    import type { TradingStrategy } from "$lib/types/TradingStrategy";

    const { userId } = $props<{ userId: number }>();

    let allStrategies: TradingStrategy[] = $state([]);
    let userStrategies: TradingStrategy[] = $state([]);
    let selectedStrategyIds: number[] = $state([]);
    let loading: boolean = $state(true);
    let saving: boolean = $state(false);
    let error: string | null = $state(null);
    let success: string | null = $state(null);

    onMount(async () => {
        await Promise.all([fetchAllStrategies(), fetchUserStrategies()]);
    });

    async function fetchAllStrategies() {
        try {
            const response = await fetch("/api/trading_strategies");

            if (!response.ok) {
                throw new Error("Failed to fetch trading strategies");
            }

            allStrategies = await response.json();
        } catch (err) {
            error = "Error loading all trading strategies";
            console.error(err);
        }
    }

    async function fetchUserStrategies() {
        try {
            const response = await fetch(
                `/api/trading_strategies/user/${userId}`,
            );

            if (!response.ok) {
                throw new Error("Failed to fetch user trading strategies");
            }

            userStrategies = await response.json();

            // Set the initial selected strategies based on user's current selections
            selectedStrategyIds = userStrategies.map((strategy) => strategy.id);
        } catch (err) {
            error = "Error loading user trading strategies";
            console.error(err);
        } finally {
            loading = false;
        }
    }

    function handleStrategySelection(strategyId: number, selected: boolean) {
        if (selected) {
            if (!selectedStrategyIds.includes(strategyId)) {
                selectedStrategyIds = [...selectedStrategyIds, strategyId];
            }
        } else {
            selectedStrategyIds = selectedStrategyIds.filter(
                (id) => id !== strategyId,
            );
        }
    }

    async function saveUserStrategies() {
        saving = true;
        error = null;
        success = null;

        try {
            const response = await fetch(
                `/api/trading_strategies/user/${userId}`,
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify({
                        strategy_ids: selectedStrategyIds,
                        clear_existing: true,
                    }),
                },
            );

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(
                    errorData.error || "Failed to save trading strategies",
                );
            }

            success = "Trading strategies updated successfully";

            // Refresh user strategies
            await fetchUserStrategies();
        } catch (err) {
            if (err instanceof Error) {
                error = err.message;
            } else {
                error = "An unknown error occurred";
            }
            console.error(err);
        } finally {
            saving = false;
        }
    }
</script>

{@render items()}

{#snippet items()}
    <div class="container mx-auto p-4">
        <h1 class="text-2xl font-bold mb-6">
            Select Trading Strategies to Follow
        </h1>

        {#if error}
            <div
                class="bg-red-100 border-l-4 border-red-500 text-red-700 p-4 mb-4"
                role="alert"
            >
                <p>{error}</p>
            </div>
        {/if}

        {#if success}
            <div
                class="bg-green-100 border-l-4 border-green-500 text-green-700 p-4 mb-4"
                role="alert"
            >
                <p>{success}</p>
            </div>
        {/if}

        <div class="bg-white shadow-md rounded px-8 pt-6 pb-8 mb-6">
            {#if loading}
                <div class="text-center py-4">
                    <p>Loading trading strategies...</p>
                </div>
            {:else if allStrategies.length === 0}
                <div class="text-center py-4">
                    <p>
                        No trading strategies available. Please contact an
                        administrator.
                    </p>
                </div>
            {:else}
                <div class="mb-6">
                    <p class="mb-2">
                        Select the trading strategies you want to follow:
                    </p>
                    <div
                        class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4"
                    >
                        {#each allStrategies as strategy}
                            <div class="p-4 border rounded">
                                <label class="flex items-start">
                                    <input
                                        type="checkbox"
                                        class="mt-1 mr-2"
                                        checked={selectedStrategyIds.includes(
                                            strategy.id,
                                        )}
                                        onchange={(e) =>
                                            handleStrategySelection(
                                                strategy.id,
                                                e.currentTarget.checked,
                                            )}
                                    />
                                    <div>
                                        <div class="font-semibold">
                                            {strategy.name}
                                        </div>
                                        {#if strategy.description}
                                            <p class="text-sm text-gray-600">
                                                {strategy.description}
                                            </p>
                                        {/if}
                                    </div>
                                </label>
                            </div>
                        {/each}
                    </div>
                </div>
                <div class="flex justify-end">
                    <button
                        class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
                        onclick={saveUserStrategies}
                        disabled={saving}
                    >
                        {saving ? "Saving..." : "Save Selections"}
                    </button>
                </div>
            {/if}
        </div>

        <div class="bg-white shadow-md rounded px-8 pt-6 pb-8">
            <h2 class="text-xl font-semibold mb-4">
                Your Current Trading Strategies
            </h2>

            {#if loading}
                <div class="text-center py-4">
                    <p>Loading your strategies...</p>
                </div>
            {:else if userStrategies.length === 0}
                <div class="text-center py-4">
                    <p>You are not following any trading strategies yet.</p>
                </div>
            {:else}
                <ul class="list-disc list-inside">
                    {#each userStrategies as strategy}
                        <li class="mb-2">
                            <span class="font-medium">{strategy.name}</span>
                            {#if strategy.description}
                                <span class="text-gray-600">
                                    - {strategy.description}</span
                                >
                            {/if}
                        </li>
                    {/each}
                </ul>
            {/if}
        </div>
    </div>
{/snippet}
