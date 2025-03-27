<script lang="ts">
    import TradePairComponentManager from "$lib/components/TradePairComponentManager.svelte";
    import type { PageData } from "../trade-pairs/$types";

    let { data }: { data: PageData } = $props();
</script>

<TradePairComponentManager initialPairs={data.pairs ?? []} />
