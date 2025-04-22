<script lang="ts">
    import type { PropFirm } from "$lib/types/PropFirms";
    import PropFirmHeader from "./PropFirmHeader.svelte";
    import AccountInformation from "./AccountInformation.svelte";
    import TradePairs from "./TradePairs.svelte";
    import RecentTrades from "./RecentTrades.svelte";

    const props = $props<{
        firm: PropFirm;
        syncing: boolean;
        onSync: (firmId: number) => void;
    }>();
</script>

<div class="bg-white rounded-lg shadow-sm overflow-hidden">
    <PropFirmHeader
        firm={props.firm}
        syncing={props.syncing}
        onSync={props.onSync}
    />
    <AccountInformation firm={props.firm} />
    <TradePairs trade_pairs={props.firm.tradePairs} />
    <RecentTrades trades={props.firm.trades} />
</div>
