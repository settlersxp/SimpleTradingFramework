<script lang="ts">
    import type { PropFirm, TradePairInfo } from "$lib/types/PropFirms";

    const props = $props<{ firm: PropFirm }>();
</script>

<div class="px-6 py-4 border-b border-gray-200">
    <h3 class="text-lg font-medium text-gray-900 mb-4">
        Associated Trade Pairs
    </h3>
    <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
        {#if props.firm.tradePairs && Array.isArray(props.firm.tradePairs.trade_pairs)}
            {#each props.firm.tradePairs.trade_pairs.filter((pair: TradePairInfo) => pair.is_associated) as pair}
                <div class="bg-gray-50 rounded p-3">
                    <p class="text-sm font-medium text-gray-900">
                        {pair.name}
                    </p>
                    {#if pair.current_label}
                        <p class="text-xs text-gray-500">
                            Label: {pair.current_label}
                        </p>
                    {/if}
                </div>
            {/each}
        {:else if props.firm.tradePairs && Array.isArray(props.firm.tradePairs)}
            <p class="text-sm text-gray-500">No trade pairs associated</p>
        {:else}
            <p class="text-sm text-gray-500">No trade pairs data available</p>
        {/if}
    </div>
</div>
