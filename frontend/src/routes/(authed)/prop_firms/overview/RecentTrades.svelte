<script lang="ts">
    import type { Trade } from "$lib/types/Trade";

    // We now expect an array of trades directly
    const props = $props<{ trades: Trade[] }>();

    // Helper function to determine if the order is a buy or sell
    function getOrderTypeDisplay(orderType: string) {
        return orderType === "0" || orderType === "sell" || orderType === "SELL"
            ? "SELL"
            : "BUY";
    }

    // Helper function to determine the order type class
    function getOrderTypeClass(orderType: string) {
        return orderType === "0" || orderType === "sell" || orderType === "SELL"
            ? "bg-red-100 text-red-800"
            : "bg-green-100 text-green-800";
    }
</script>

<div class="px-6 py-4">
    <h3 class="text-lg font-medium text-gray-900 mb-4">Recent Trades</h3>

    {#if Array.isArray(props.trades) && props.trades.length > 0}
        <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200">
                <thead>
                    <tr>
                        <th
                            class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase"
                            >ID</th
                        >
                        <th
                            class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase"
                            >Strategy</th
                        >
                        <th
                            class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase"
                            >Type</th
                        >
                        <th
                            class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase"
                            >Ticker</th
                        >
                        <th
                            class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase"
                            >Contracts</th
                        >
                        <th
                            class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase"
                            >Position Size</th
                        >
                        <th
                            class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase"
                            >Date</th
                        >
                    </tr>
                </thead>
                <tbody class="divide-y divide-gray-200">
                    {#each props.trades as trade}
                        <tr class="hover:bg-gray-50">
                            <td class="px-4 py-3 text-sm text-gray-900"
                                >{trade.id}</td
                            >
                            <td class="px-4 py-3 text-sm text-gray-900"
                                >{trade.strategy}</td
                            >
                            <td class="px-4 py-3">
                                <span
                                    class={`px-2 py-1 text-xs font-medium rounded-full ${getOrderTypeClass(trade.order_type)}`}
                                >
                                    {getOrderTypeDisplay(trade.order_type)}
                                </span>
                            </td>
                            <td class="px-4 py-3 text-sm text-gray-900"
                                >{trade.ticker}</td
                            >
                            <td class="px-4 py-3 text-sm text-gray-900"
                                >{typeof trade.contracts === "number"
                                    ? trade.contracts.toFixed(3)
                                    : trade.contracts}</td
                            >
                            <td class="px-4 py-3 text-sm text-gray-900"
                                >${typeof trade.position_size === "number"
                                    ? trade.position_size.toFixed(2)
                                    : trade.position_size}</td
                            >
                            <td class="px-4 py-3 text-sm text-gray-900"
                                >{new Date(
                                    trade.created_at,
                                ).toLocaleString()}</td
                            >
                        </tr>
                    {/each}
                </tbody>
            </table>
        </div>
    {:else}
        <p class="text-sm text-gray-500">No trades found</p>
    {/if}
</div>
