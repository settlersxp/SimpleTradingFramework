<script lang="ts">
    import type { PropFirm } from "$lib/types/PropFirms";

    const props = $props<{ firm: PropFirm }>();
</script>

<div class="px-6 py-4">
    <h3 class="text-lg font-medium text-gray-900 mb-4">Recent Trades</h3>
    {#if props.firm.trades && props.firm.trades.length > 0}
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
                    {#each props.firm.trades as trade}
                        <tr class="hover:bg-gray-50">
                            <td class="px-4 py-3 text-sm text-gray-900"
                                >{trade.id}</td
                            >
                            <td class="px-4 py-3 text-sm text-gray-900"
                                >{trade.strategy}</td
                            >
                            <td class="px-4 py-3">
                                <span
                                    class={`px-2 py-1 text-xs font-medium rounded-full ${trade.order_type === "buy" ? "bg-green-100 text-green-800" : "bg-red-100 text-red-800"}`}
                                >
                                    {trade.order_type.toUpperCase()}
                                </span>
                            </td>
                            <td class="px-4 py-3 text-sm text-gray-900"
                                >{trade.ticker}</td
                            >
                            <td class="px-4 py-3 text-sm text-gray-900"
                                >{trade.contracts.toFixed(3)}</td
                            >
                            <td class="px-4 py-3 text-sm text-gray-900"
                                >${trade.position_size.toFixed(2)}</td
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
