<script lang="ts">
    import type { Trade } from "$lib/types/Trade";

    // We expect an array of trades via props
    const props = $props<{ trades: Trade[] }>();

    // Local reactive copy of trades so we can update the UI after close/delete without mutating props
    let trades = $state<Trade[]>([...props.trades]);

    // Keep local state in sync if the parent sends new trades
    $effect(() => {
        if (
            props.trades !== undefined &&
            props.trades.length !== trades.length
        ) {
            trades = [...props.trades];
        }
    });

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

    function removeTradeFromList(trade: Trade) {
        // Try to remove by id first, fallback to platform_id if id is undefined
        trades = trades.filter(
            (t) =>
                (trade.id !== undefined && t.id !== trade.id) ||
                (trade.id === undefined && t.platform_id !== trade.platform_id),
        );
    }

    async function closeTrade(trade: Trade) {
        try {
            const response = await fetch(`/api/trades/close`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    platform_id: trade.platform_id,
                    prop_firm_id: trade.prop_firm_id,
                }),
            });

            if (!response.ok) {
                throw new Error("Failed to close trade");
            }

            // Optimistically remove trade from local list on success
            removeTradeFromList(trade);
        } catch (error) {
            console.error("Error closing trade:", error);
        }
    }

    async function deleteTrade(trade: Trade) {
        const url = `/api/trades/${trade.signal_id}/prop_firm/${trade.prop_firm_id}`;
        console.log("URL in deleteTrade:", url);
        try {
            const response = await fetch(url, {
                method: "DELETE",
            });

            console.log("Response:", response);
            if (!response.ok) {
                throw new Error("Failed to delete trade");
            }

            // Remove the deleted trade from the local state so UI updates
            removeTradeFromList(trade);
        } catch (error) {
            console.error("Error deleting trade:", error);
        }
    }
</script>

<div class="px-6 py-4">
    <h3 class="text-lg font-medium text-gray-900 mb-4">Recent Trades</h3>

    {#if Array.isArray(trades) && trades.length > 0}
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
                        <th
                            class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase"
                            >Actions</th
                        >
                    </tr>
                </thead>
                <tbody class="divide-y divide-gray-200">
                    {#each trades as trade}
                        <tr class="hover:bg-gray-50">
                            <td class="px-4 py-3 text-sm text-gray-900"
                                >{trade.platform_id}</td
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
                            <td class="px-4 py-3 text-sm text-gray-900">
                                <button
                                    class="text-blue-500 hover:text-blue-700"
                                    onclick={() => {
                                        closeTrade(trade);
                                    }}
                                >
                                    Close
                                </button>
                                <button
                                    class="text-blue-500 hover:text-blue-700"
                                    onclick={() => {
                                        deleteTrade(trade);
                                    }}
                                >
                                    Delete
                                </button>
                            </td>
                        </tr>
                    {/each}
                </tbody>
            </table>
        </div>
    {:else}
        <p class="text-sm text-gray-500">No trades found</p>
    {/if}
</div>
