<script lang="ts">
    import type { TradePairInfo } from "$lib/types/PropFirms";

    const props = $props<{ trade_pairs: TradePairInfo[] | any[] }>();

    // Helper function to check if there are any associated pairs
    function hasAssociatedPairs(pairs: any[]): boolean {
        return (
            Array.isArray(pairs) &&
            pairs.some((pair: any) => pair.is_associated)
        );
    }

    const hasAssociated = hasAssociatedPairs(props.trade_pairs);
</script>

<div class="px-6 py-4 border-b border-gray-200">
    <h3 class="text-lg font-medium text-gray-900 mb-4">
        Associated Trade Pairs
    </h3>
    <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
        {#if Array.isArray(props.trade_pairs) && props.trade_pairs.length > 0 && hasAssociated}
            {#each props.trade_pairs.filter((pair: TradePairInfo | any) => pair.is_associated) as pair}
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
        {:else}
            <p class="text-sm text-gray-500">No trade pairs associated</p>
        {/if}
    </div>
</div>
