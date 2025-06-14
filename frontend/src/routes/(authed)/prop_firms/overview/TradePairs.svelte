<script lang="ts">
    import type { TradePairInfo } from "$lib/types/PropFirms";

    const props = $props<{
        trade_pairs: TradePairInfo[] | any[];
        prop_firm_id: number;
        onDelete: (firmId: number, pairId: number) => void;
    }>();

    // Helper function to check if there are any associated pairs
    function hasAssociatedPairs(pairs: any[]): boolean {
        return (
            Array.isArray(pairs) &&
            pairs.some((pair: any) => pair.is_associated)
        );
    }

    async function deleteTradePair(pairId: number) {
        const response = await fetch(
            `/python/prop_firms/${props.prop_firm_id}/trade_pairs/${pairId}`,
            {
                method: "DELETE",
            },
        );

        if (!response.ok) {
            throw new Error("Failed to delete trade pair", {
                cause: response.body,
            });
        }

        props.onDelete(props.prop_firm_id, pairId);
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
                    <button
                        class="bg-red-500 hover:bg-red-700 text-white font-bold py-1 px-2 rounded text-xs"
                        onclick={() => deleteTradePair(pair.id)}
                    >
                        X
                    </button>
                </div>
            {/each}
        {:else}
            <p class="text-sm text-gray-500">No trade pairs associated</p>
        {/if}
    </div>
</div>
