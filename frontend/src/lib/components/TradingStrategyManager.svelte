<script lang="ts">
    import { onMount } from "svelte";
    import type { TradingStrategy } from "$lib/types/TradingStrategy";

    let strategies: TradingStrategy[] = $state([]);
    let loading: boolean = $state(true);
    let error: string | null = $state(null);
    let editingStrategy: TradingStrategy | null = $state(null);
    let newStrategyName: string = $state("");
    let newStrategyDescription: string = $state("");

    onMount(async () => {
        await fetchStrategies();
    });

    async function fetchStrategies() {
        loading = true;
        error = null;

        try {
            const response = await fetch("/api/trading_strategies");

            if (!response.ok) {
                throw new Error("Failed to fetch trading strategies");
            }

            const data = await response.json();
            strategies = data;
        } catch (err) {
            error = "Error loading trading strategies";
            console.error(err);
        } finally {
            loading = false;
        }
    }

    async function createStrategy(event: Event) {
        event.preventDefault();

        if (!newStrategyName.trim()) {
            error = "Strategy name is required";
            return;
        }

        try {
            const response = await fetch("/api/trading_strategies", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    name: newStrategyName,
                    description: newStrategyDescription || null,
                }),
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || "Failed to create strategy");
            }

            // Reset form
            newStrategyName = "";
            newStrategyDescription = "";

            // Refresh strategies list
            await fetchStrategies();
        } catch (err) {
            if (err instanceof Error) {
                error = err.message;
            } else {
                error = "An unknown error occurred";
            }
            console.error(err);
        }
    }

    function startEditStrategy(strategy: TradingStrategy) {
        editingStrategy = { ...strategy };
    }

    async function updateStrategy(event: Event) {
        event.preventDefault();

        if (!editingStrategy) return;

        if (!editingStrategy.name.trim()) {
            error = "Strategy name is required";
            return;
        }

        try {
            const response = await fetch(
                `/api/trading_strategies/${editingStrategy.id}`,
                {
                    method: "PUT",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify({
                        name: editingStrategy.name,
                        description: editingStrategy.description,
                    }),
                },
            );

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || "Failed to update strategy");
            }

            // Reset editing state
            editingStrategy = null;

            // Refresh strategies list
            await fetchStrategies();
        } catch (err) {
            if (err instanceof Error) {
                error = err.message;
            } else {
                error = "An unknown error occurred";
            }
            console.error(err);
        }
    }

    async function deleteStrategy(strategyId: number) {
        if (
            !confirm("Are you sure you want to delete this trading strategy?")
        ) {
            return;
        }

        try {
            const response = await fetch(
                `/api/trading_strategies/${strategyId}`,
                {
                    method: "DELETE",
                },
            );

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || "Failed to delete strategy");
            }

            // Refresh strategies list
            await fetchStrategies();
        } catch (err) {
            if (err instanceof Error) {
                error = err.message;
            } else {
                error = "An unknown error occurred";
            }
            console.error(err);
        }
    }

    function cancelEdit() {
        editingStrategy = null;
    }
</script>

{@render items()}

{#snippet items()}
    <div class="container mx-auto p-4">
        <h1 class="text-2xl font-bold mb-6">Trading Strategies Management</h1>

        {#if error}
            <div
                class="bg-red-100 border-l-4 border-red-500 text-red-700 p-4 mb-4"
                role="alert"
            >
                <p>{error}</p>
            </div>
        {/if}

        <!-- Add New Strategy Form -->
        <div class="bg-white shadow-md rounded px-8 pt-6 pb-8 mb-6">
            <h2 class="text-xl font-semibold mb-4">Add New Trading Strategy</h2>
            <form onsubmit={createStrategy}>
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
                        type="text"
                        placeholder="Enter strategy name"
                        value={newStrategyName}
                        onchange={(e) =>
                            (newStrategyName = e.currentTarget.value)}
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
                        placeholder="Enter strategy description"
                        value={newStrategyDescription}
                        onchange={(e) =>
                            (newStrategyDescription = e.currentTarget.value)}
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
                            {#each strategies as strategy}
                                {#if editingStrategy && editingStrategy.id === strategy.id}
                                    <tr class="bg-blue-50">
                                        <td
                                            class="border px-4 py-2"
                                            colspan="4"
                                        >
                                            <form onsubmit={updateStrategy}>
                                                <div
                                                    class="flex flex-wrap -mx-2"
                                                >
                                                    <div class="px-2 w-1/3">
                                                        <input
                                                            class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                                                            type="text"
                                                            placeholder="Strategy name"
                                                            value={editingStrategy.name ||
                                                                ""}
                                                            onchange={(e) => {
                                                                editingStrategy.name =
                                                                    e.currentTarget.value;
                                                            }}
                                                            required
                                                        />
                                                    </div>
                                                    <div class="px-2 w-1/3">
                                                        <input
                                                            class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                                                            type="text"
                                                            placeholder="Description (optional)"
                                                            value={editingStrategy.description ||
                                                                ""}
                                                            onchange={(e) => {
                                                                editingStrategy.description =
                                                                    e.currentTarget.value;
                                                            }}
                                                        />
                                                    </div>
                                                    <div
                                                        class="px-2 w-1/3 flex"
                                                    >
                                                        <button
                                                            type="submit"
                                                            class="bg-green-500 hover:bg-green-700 text-white font-bold py-1 px-2 rounded mr-2 focus:outline-none focus:shadow-outline"
                                                        >
                                                            Save
                                                        </button>
                                                        <button
                                                            type="button"
                                                            onclick={cancelEdit}
                                                            class="bg-gray-500 hover:bg-gray-700 text-white font-bold py-1 px-2 rounded focus:outline-none focus:shadow-outline"
                                                        >
                                                            Cancel
                                                        </button>
                                                    </div>
                                                </div>
                                            </form>
                                        </td>
                                    </tr>
                                {:else}
                                    <tr>
                                        <td class="border px-4 py-2"
                                            >{strategy.name}</td
                                        >
                                        <td class="border px-4 py-2"
                                            >{strategy.description || "-"}</td
                                        >
                                        <td class="border px-4 py-2"
                                            >{new Date(
                                                strategy.created_at,
                                            ).toLocaleDateString()}</td
                                        >
                                        <td class="border px-4 py-2">
                                            <button
                                                onclick={() =>
                                                    startEditStrategy(strategy)}
                                                class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-1 px-2 rounded mr-2 focus:outline-none focus:shadow-outline"
                                            >
                                                Edit
                                            </button>
                                            <button
                                                onclick={() =>
                                                    deleteStrategy(strategy.id)}
                                                class="bg-red-500 hover:bg-red-700 text-white font-bold py-1 px-2 rounded focus:outline-none focus:shadow-outline"
                                            >
                                                Delete
                                            </button>
                                        </td>
                                    </tr>
                                {/if}
                            {/each}
                        </tbody>
                    </table>
                </div>
            {/if}
        </div>
    </div>
{/snippet}
