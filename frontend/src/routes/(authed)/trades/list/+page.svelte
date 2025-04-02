<script lang="ts">
    import { onMount } from "svelte";

    type TradeWithFirm = {
        id: number;
        strategy: string;
        order_type: string;
        contracts: number;
        ticker: string;
        position_size: number;
        created_at: string;
        prop_firm: {
            id: number;
            name: string;
            available_balance: number;
            dowdown_percentage: number;
        };
    };

    let tradesWithFirms = $state<TradeWithFirm[]>([]);
    let loading = $state(true);
    let error = $state<string | null>(null);

    onMount(() => {
        const fetchData = async () => {
            try {
                const response = await fetch("/api/trades/view");
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                const data = await response.json();
                tradesWithFirms = data.trades_with_firms;
            } catch (e) {
                error = e instanceof Error ? e.message : "An error occurred";
                console.error("Error fetching trades with firms:", e);
            } finally {
                loading = false;
            }
        };

        fetchData();

        // Set up auto-refresh every 5 seconds
        const intervalId = setInterval(fetchData, 5000);

        // Return cleanup function directly (not from async)
        return () => clearInterval(intervalId);
    });
</script>

<div class="min-h-screen bg-gray-100 p-8">
    <div class="max-w-7xl mx-auto">
        <div class="bg-white rounded-lg shadow-sm">
            <div
                class="px-6 py-4 border-b border-gray-200 bg-gray-50 flex justify-between items-center"
            >
                <h2 class="text-xl font-semibold text-gray-800">Trades</h2>
                <a
                    href="/prop_firms/list"
                    class="bg-gray-500 hover:bg-gray-700 text-white font-bold py-2 px-4 rounded"
                >
                    View Prop Firms
                </a>
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
                                    >Prop Firm</th
                                >
                            </tr>
                        </thead>
                        <tbody class="bg-white divide-y divide-gray-200">
                            {#each tradesWithFirms as trade}
                                <tr class="hover:bg-gray-50 transition-colors">
                                    <td
                                        class="px-6 py-4 whitespace-nowrap text-sm text-gray-900"
                                        >{trade.id}</td
                                    >
                                    <td
                                        class="px-6 py-4 whitespace-nowrap text-sm text-gray-900"
                                        >{trade.strategy}</td
                                    >
                                    <td class="px-6 py-4 whitespace-nowrap">
                                        <span
                                            class="px-2 py-1 text-xs font-semibold rounded-full {trade.order_type ===
                                            'buy'
                                                ? 'bg-green-100 text-green-800'
                                                : 'bg-red-100 text-red-800'}"
                                        >
                                            {trade.order_type.toUpperCase()}
                                        </span>
                                    </td>
                                    <td
                                        class="px-6 py-4 whitespace-nowrap text-sm text-gray-900"
                                        >{trade.contracts.toFixed(3)}</td
                                    >
                                    <td
                                        class="px-6 py-4 whitespace-nowrap text-sm text-gray-900"
                                        >{trade.ticker}</td
                                    >
                                    <td
                                        class="px-6 py-4 whitespace-nowrap text-sm text-gray-900"
                                        >${trade.position_size.toFixed(2)}</td
                                    >
                                    <td
                                        class="px-6 py-4 whitespace-nowrap text-sm text-gray-900"
                                        >{new Date(
                                            trade.created_at,
                                        ).toLocaleString()}</td
                                    >
                                    <td
                                        class="px-6 py-4 whitespace-nowrap text-sm text-gray-900"
                                        >{trade.prop_firm.name}</td
                                    >
                                </tr>
                            {:else}
                                <tr>
                                    <td
                                        colspan="8"
                                        class="px-6 py-4 text-center text-sm text-gray-500"
                                        >No trades found</td
                                    >
                                </tr>
                            {/each}
                        </tbody>
                    </table>
                </div>
            {/if}
        </div>
    </div>
</div>
