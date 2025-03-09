<script lang="ts">
    import { onMount } from "svelte";

    type Trade = {
        id: number;
        strategy: string;
        order_type: string;
        contracts: number;
        ticker: string;
        position_size: number;
        created_at: string;
        response: any;
    };

    let trades = $state<Trade[]>([]);
    let loading = $state(true);
    let error = $state<string | null>(null);

    onMount(async () => {
        try {
            const response = await fetch("/api/trades/list");
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            trades = data.trades;
        } catch (e) {
            error = e instanceof Error ? e.message : "An error occurred";
            console.error("Error fetching trades:", e);
        } finally {
            loading = false;
        }
    });

    async function deleteTrade(tradeId: number) {
        if (!confirm("Are you sure you want to delete this trade?")) {
            return;
        }

        try {
            const response = await fetch(`/api/trades/${tradeId}`, {
                method: "DELETE",
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            // Remove the deleted trade from the list
            trades = trades.filter((trade) => trade.id !== tradeId);
        } catch (e) {
            error = e instanceof Error ? e.message : "Error deleting trade";
            console.error("Error deleting trade:", e);
        }
    }

    async function replayTrade(tradeId: number) {
        try {
            const response = await fetch(`/api/trades/${tradeId}/replay`, {
                method: "POST",
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            alert(data.message || "Trade replayed successfully");
        } catch (e) {
            error = e instanceof Error ? e.message : "Error replaying trade";
            console.error("Error replaying trade:", e);
        }
    }

    async function closeTrade(tradeId: number) {
        try {
            const response = await fetch(
                `/api/trades/close?trade_id=${tradeId}`,
                {
                    method: "GET",
                },
            );

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            alert(data.message || "Trade closed successfully");

            // Refresh the trades list
            const tradesResponse = await fetch("/api/trades/list");
            if (tradesResponse.ok) {
                const tradesData = await tradesResponse.json();
                trades = tradesData.trades;
            }
        } catch (e) {
            error = e instanceof Error ? e.message : "Error closing trade";
            console.error("Error closing trade:", e);
        }
    }
</script>

<div class="min-h-screen bg-gray-100 p-8">
    <div class="max-w-7xl mx-auto">
        <div class="bg-white rounded-lg shadow-sm">
            <div class="px-6 py-4 border-b border-gray-200 bg-gray-50">
                <h2 class="text-xl font-semibold text-gray-800">Trades List</h2>
            </div>

            {#if loading}
                <div class="flex justify-center items-center p-8">
                    <div
                        class="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-500"
                    ></div>
                </div>
            {:else if error}
                <div
                    class="p-4 bg-red-100 text-red-700 border-l-4 border-red-500"
                >
                    <p>{error}</p>
                </div>
            {:else}
                <div class="overflow-x-auto">
                    <table class="min-w-full divide-y divide-gray-200">
                        <thead class="bg-gray-50">
                            <tr>
                                <th
                                    class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                                    >Actions</th
                                >
                                <th
                                    class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                                    >ID</th
                                >
                                <th
                                    class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                                    >Strategy</th
                                >
                                <th
                                    class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                                    >Order Type</th
                                >
                                <th
                                    class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                                    >Contracts</th
                                >
                                <th
                                    class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                                    >Ticker</th
                                >
                                <th
                                    class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                                    >Position Size</th
                                >
                                <th
                                    class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                                    >Created At</th
                                >
                                <th
                                    class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                                    >MT5 ID</th
                                >
                            </tr>
                        </thead>
                        <tbody class="bg-white divide-y divide-gray-200">
                            {#each trades as trade}
                                <tr class="hover:bg-gray-50 transition-colors">
                                    <td class="px-6 py-4 whitespace-nowrap">
                                        <div class="flex space-x-2">
                                            <button
                                                class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-1 px-2 rounded text-xs"
                                                onclick={() =>
                                                    replayTrade(trade.id)}
                                            >
                                                <svg
                                                    xmlns="http://www.w3.org/2000/svg"
                                                    class="h-4 w-4"
                                                    fill="none"
                                                    viewBox="0 0 24 24"
                                                    stroke="currentColor"
                                                >
                                                    <path
                                                        stroke-linecap="round"
                                                        stroke-linejoin="round"
                                                        stroke-width="2"
                                                        d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z"
                                                    />
                                                    <path
                                                        stroke-linecap="round"
                                                        stroke-linejoin="round"
                                                        stroke-width="2"
                                                        d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                                                    />
                                                </svg>
                                            </button>
                                            <button
                                                class="bg-yellow-500 hover:bg-yellow-700 text-white font-bold py-1 px-2 rounded text-xs"
                                                onclick={() =>
                                                    closeTrade(trade.id)}
                                            >
                                                Close
                                            </button>
                                            <button
                                                class="bg-red-500 hover:bg-red-700 text-white font-bold py-1 px-2 rounded text-xs"
                                                onclick={() =>
                                                    deleteTrade(trade.id)}
                                            >
                                                Delete
                                            </button>
                                        </div>
                                    </td>
                                    <td
                                        class="px-6 py-4 whitespace-nowrap text-sm text-gray-900"
                                        >{trade.id}</td
                                    >
                                    <td
                                        class="px-6 py-4 whitespace-nowrap text-sm text-gray-900"
                                        >{trade.strategy}</td
                                    >
                                    <td
                                        class="px-6 py-4 whitespace-nowrap text-sm text-gray-900"
                                        >{trade.order_type}</td
                                    >
                                    <td
                                        class="px-6 py-4 whitespace-nowrap text-sm text-gray-900"
                                        >{trade.contracts}</td
                                    >
                                    <td
                                        class="px-6 py-4 whitespace-nowrap text-sm text-gray-900"
                                        >{trade.ticker}</td
                                    >
                                    <td
                                        class="px-6 py-4 whitespace-nowrap text-sm text-gray-900"
                                        >{trade.position_size}</td
                                    >
                                    <td
                                        class="px-6 py-4 whitespace-nowrap text-sm text-gray-900"
                                        >{trade.created_at}</td
                                    >
                                    <td
                                        class="px-6 py-4 whitespace-nowrap text-sm text-gray-900"
                                    >
                                        {#if trade.response && trade.response[2]}
                                            {trade.response[2]}
                                        {/if}
                                    </td>
                                </tr>
                            {/each}
                        </tbody>
                    </table>
                </div>
            {/if}
        </div>
    </div>
</div>
