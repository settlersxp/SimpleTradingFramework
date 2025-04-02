<script lang="ts">
    import type { Trade } from "$lib/types/Trade";
    let { trade } = $props<{ trade: Trade }>();

    let error = $state<string | null>(null);
    let trades = $state<Trade[]>([]);
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

<tr class="hover:bg-gray-50 transition-colors">
    <td class="px-6 py-4 whitespace-nowrap">
        <div class="flex space-x-2">
            <button
                class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-1 px-2 rounded text-xs"
                onclick={() =>
                    replayTrade(trade.id)}
                aria-label="Replay Trade"
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
                aria-label="Close Trade"
            >
                Close
            </button>
            <button
                class="bg-red-500 hover:bg-red-700 text-white font-bold py-1 px-2 rounded text-xs"
                onclick={() =>
                    deleteTrade(trade.id)}
                aria-label="Delete Trade"
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