<script lang="ts">
    import { enhance } from "$app/forms";
    import type { ActionData, PageData } from "./$types";

    let { data, form }: { data: PageData; form: ActionData } = $props();

    // Initialize selected IDs based on initially loaded user strategies
    let selectedStrategyIds: number[] = $state(
        data.userStrategies?.map((s) => s.id) ?? [],
    );

    // Reactive statement to update selected IDs if data changes (e.g., after form submission)
    $effect(() => {
        selectedStrategyIds = data.userStrategies?.map((s) => s.id) ?? [];
    });

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
        // No need to call saveUserStrategies here, submission handles it
    }
</script>

<div class="container mx-auto px-4 py-8">
    <h1 class="text-3xl font-bold mb-8">My Trading Strategies</h1>
    <p class="mb-6">
        Select the trading strategies you want to follow and track in your
        account.
    </p>

    <!-- Data Loading Error Display -->
    {#if data.error}
        <div
            class="bg-red-100 border-l-4 border-red-500 text-red-700 p-4 mb-4"
            role="alert"
        >
            <p>Error loading data: {data.error}</p>
        </div>
    {/if}

    <!-- Form Submission Status/Error Display -->
    {#if form?.error}
        <div
            class="bg-red-100 border-l-4 border-red-500 text-red-700 p-4 mb-4"
            role="alert"
        >
            <p>Error saving: {form.error}</p>
        </div>
    {/if}

    {#if form?.success}
        <div
            class="bg-green-100 border-l-4 border-green-500 text-green-700 p-4 mb-4"
            role="alert"
        >
            <p>{form.success}</p>
        </div>
    {/if}

    <form
        method="POST"
        use:enhance={() => {
            // Optional: Add logic before/after form submission
            // e.g., disable button, show loading indicator
            return async ({ update }) => {
                // This runs after the server action completes
                await update(); // Refreshes data based on server response
            };
        }}
        class="bg-white rounded-lg shadow mb-6"
    >
        <div class="px-8 pt-6 pb-8">
            <h2 class="text-xl font-semibold mb-4">
                Available Trading Strategies
            </h2>

            {#if !data.allStrategies || data.allStrategies.length === 0}
                <div class="text-center py-4">
                    <p>
                        No trading strategies available or failed to load.
                        Please contact an administrator.
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
                        {#each data.allStrategies as strategy (strategy.id)}
                            <div class="p-4 border rounded">
                                <label class="flex items-start">
                                    <input
                                        type="checkbox"
                                        name="strategy_ids"
                                        value={strategy.id}
                                        class="mt-1 mr-2"
                                        checked={selectedStrategyIds.includes(
                                            strategy.id,
                                        )}
                                        onchange={(e: Event) =>
                                            handleStrategySelection(
                                                strategy.id,
                                                (
                                                    e.currentTarget as HTMLInputElement
                                                ).checked,
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
                        type="submit"
                        class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
                    >
                        Save Selections
                    </button>
                </div>
            {/if}
        </div>
    </form>

    <div class="bg-white shadow-md rounded px-8 pt-6 pb-8">
        <h2 class="text-xl font-semibold mb-4">
            Your Current Trading Strategies
        </h2>

        {#if !data.userStrategies || data.userStrategies.length === 0}
            <div class="text-center py-4">
                {#if data.error}
                    <p>Could not load your strategies due to an error.</p>
                {:else}
                    <p>You are not following any trading strategies yet.</p>
                {/if}
            </div>
        {:else}
            <ul class="list-disc list-inside">
                {#each data.userStrategies as strategy (strategy.id)}
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
