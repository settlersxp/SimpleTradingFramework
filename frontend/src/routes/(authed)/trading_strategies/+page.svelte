<script lang="ts">
    import { enhance } from "$app/forms";
    import { invalidateAll } from "$app/navigation";
    import type { TradingStrategiesPageData } from "$lib/types/TradingStrategyPageData";
    import StrategyRow from "./StrategyRow.svelte";
    // Props: data from load function, form for action results
    let { data }: { data: TradingStrategiesPageData } = $props();
    let form: any = $state(); // Declare form as state

    let editingStrategyId: number | null = $state(null);

    // Reactive statements to access loaded data
    let strategies = $derived(data.strategies);
    let loading = $derived(data.loading);
    let pageError = $derived(data.error); // Renamed to avoid conflict with form error

    // Function to handle successful form submissions
    function handleSuccess() {
        editingStrategyId = null; // Close edit form on success
        invalidateAll(); // Re-run load function to refresh data
        // Clear potential form errors from previous submissions
        // form = null; // No longer needed to manually clear, SvelteKit handles it with enhance
    }
</script>

<div class="container mx-auto px-4 py-8">
    <h1 class="text-3xl font-bold mb-8">Trading Strategies Management</h1>
    <div class="bg-white rounded-lg shadow p-6">
        {#if pageError}
            <div
                class="bg-red-100 border-l-4 border-red-500 text-red-700 p-4 mb-4"
                role="alert"
            >
                <p>{pageError}</p>
            </div>
        {/if}

        {#if form?.error}
            <div
                class="bg-red-100 border-l-4 border-red-500 text-red-700 p-4 mb-4"
                role="alert"
            >
                <p>Error: {form.error}</p>
            </div>
        {/if}

        <!-- Add New Strategy Form -->
        <div class="bg-white shadow-md rounded px-8 pt-6 pb-8 mb-6">
            <h2 class="text-xl font-semibold mb-4">Add New Trading Strategy</h2>
            <form
                method="POST"
                action="?/create"
                use:enhance={() => {
                    return async ({ result }) => {
                        if (result.type === "success") {
                            handleSuccess();
                            // Optionally clear form fields here if needed
                            const formEl = document.querySelector(
                                "#add-strategy-form",
                            ) as HTMLFormElement;
                            if (formEl) formEl.reset();
                        }
                    };
                }}
                id="add-strategy-form"
            >
                <div class="mb-4">
                    <label
                        class="block text-gray-700 text-sm font-bold mb-2"
                        for="strategyName"
                    >
                        Strategy Name
                    </label>
                    <input
                        class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                        id="strategyName"
                        name="name"
                        type="text"
                        placeholder="Enter strategy name"
                        required
                    />
                </div>
                <div class="mb-4">
                    <label
                        class="block text-gray-700 text-sm font-bold mb-2"
                        for="strategyDescription"
                    >
                        Description (Optional)
                    </label>
                    <textarea
                        class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 mb-3 leading-tight focus:outline-none focus:shadow-outline"
                        id="strategyDescription"
                        name="description"
                        placeholder="Enter strategy description"
                    ></textarea>
                </div>
                <div class="flex items-center justify-between">
                    <button
                        class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
                        type="submit"
                    >
                        Add Strategy
                    </button>
                </div>
            </form>
        </div>

        <!-- Strategies List -->
        <div class="bg-white shadow-md rounded px-8 pt-6 pb-8">
            <h2 class="text-xl font-semibold mb-4">Trading Strategies</h2>

            {#if loading}
                <div class="text-center py-4">
                    <p>Loading trading strategies...</p>
                </div>
            {:else if strategies.length === 0}
                <div class="text-center py-4">
                    <p>
                        No trading strategies found. Add your first one above.
                    </p>
                </div>
            {:else}
                <div class="overflow-x-auto">
                    <table class="w-full table-auto">
                        <thead>
                            <tr class="bg-gray-100">
                                <th class="px-4 py-2 text-left">Name</th>
                                <th class="px-4 py-2 text-left">Description</th>
                                <th class="px-4 py-2 text-left">Created</th>
                                <th class="px-4 py-2 text-left">Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {#each strategies as strategy (strategy.id)}
                                <StrategyRow {strategy} />
                            {/each}
                        </tbody>
                    </table>
                </div>
            {/if}
        </div>
    </div>
</div>
