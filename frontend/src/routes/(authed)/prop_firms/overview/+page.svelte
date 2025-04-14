<script lang="ts">
    import type { PropFirm, TradePairInfo } from "$lib/types/PropFirms";

    const props = $props<{ data: { propFirms: PropFirm[] } }>();
    let syncing = $state(false);
    let syncError = $state<string | null>(null);

    async function syncPropFirm(firmId: number) {
        syncing = true;
        syncError = null;
        try {
            const response = await fetch("/api/prop_firms/sync", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ prop_firm_id: firmId }),
            });

            if (!response.ok) {
                throw new Error("Failed to sync prop firm");
            }

            // Reload the page to show updated data
            window.location.reload();
        } catch (error) {
            console.error("Error syncing prop firm:", error);
            syncError =
                error instanceof Error ? error.message : "An error occurred";
        } finally {
            syncing = false;
        }
    }

    async function syncAllPropFirms() {
        syncing = true;
        syncError = null;
        try {
            const response = await fetch("/api/prop_firms/sync", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
            });

            if (!response.ok) {
                throw new Error("Failed to sync prop firms");
            }

            // Reload the page to show updated data
            window.location.reload();
        } catch (error) {
            console.error("Error syncing prop firms:", error);
            syncError =
                error instanceof Error ? error.message : "An error occurred";
        } finally {
            syncing = false;
        }
    }
</script>

<svelte:head>
    <title>Prop Firms Overview</title>
</svelte:head>

<div class="min-h-screen bg-gray-100 p-8">
    <div class="max-w-7xl mx-auto">
        <div class="mb-8">
            <div class="flex justify-between items-center">
                <div>
                    <h1 class="text-3xl font-bold text-gray-900">
                        Prop Firms Overview
                    </h1>
                    <p class="mt-2 text-gray-600">
                        Comprehensive view of all prop firms, their accounts,
                        and trades
                    </p>
                </div>
                <button
                    onclick={syncAllPropFirms}
                    disabled={syncing}
                    class="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                    {syncing ? "Syncing..." : "Sync All Prop Firms"}
                </button>
            </div>
            {#if syncError}
                <div class="mt-4 p-4 bg-red-100 text-red-700 rounded-md">
                    {syncError}
                </div>
            {/if}
        </div>

        <div class="grid grid-cols-1 gap-8">
            {#each props.data.propFirms as firm}
                <div class="bg-white rounded-lg shadow-sm overflow-hidden">
                    <!-- Firm Header -->
                    <div class="px-6 py-4 bg-gray-50 border-b border-gray-200">
                        <div class="flex justify-between items-center">
                            <h2 class="text-xl font-semibold text-gray-800">
                                {firm.name}
                            </h2>
                            <div class="flex items-center space-x-4">
                                <span
                                    class={`px-3 py-1 rounded-full text-sm font-medium ${firm.is_active ? "bg-green-100 text-green-800" : "bg-red-100 text-red-800"}`}
                                >
                                    {firm.is_active ? "Active" : "Inactive"}
                                </span>
                                <button
                                    onclick={() => syncPropFirm(firm.id)}
                                    disabled={syncing}
                                    class="bg-gray-100 text-gray-700 px-3 py-1 rounded hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed"
                                >
                                    {syncing ? "Syncing..." : "Sync"}
                                </button>
                            </div>
                        </div>
                    </div>

                    <!-- Account Information -->
                    <div class="px-6 py-4 border-b border-gray-200">
                        <h3 class="text-lg font-medium text-gray-900 mb-4">
                            Account Information
                        </h3>
                        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                            <div>
                                <p class="text-sm text-gray-500">
                                    Full Balance
                                </p>
                                <p class="text-lg font-medium text-gray-900">
                                    ${firm.full_balance.toFixed(2)}
                                </p>
                            </div>
                            <div>
                                <p class="text-sm text-gray-500">
                                    Available Balance
                                </p>
                                <p class="text-lg font-medium text-gray-900">
                                    ${firm.available_balance.toFixed(2)}
                                </p>
                            </div>
                            <div>
                                <p class="text-sm text-gray-500">
                                    Drawdown Percentage
                                </p>
                                <p class="text-lg font-medium text-gray-900">
                                    {firm.dowdown_percentage.toFixed(2)}%
                                </p>
                            </div>
                        </div>
                        <div class="mt-4 grid grid-cols-1 md:grid-cols-3 gap-4">
                            <div>
                                <p class="text-sm text-gray-500">Platform</p>
                                <p class="text-lg font-medium text-gray-900">
                                    {firm.platform_type}
                                </p>
                            </div>
                            <div>
                                <p class="text-sm text-gray-500">Server</p>
                                <p class="text-lg font-medium text-gray-900">
                                    {firm.ip_address}:{firm.port}
                                </p>
                            </div>
                        </div>
                    </div>

                    <!-- Trade Pairs -->
                    <div class="px-6 py-4 border-b border-gray-200">
                        <h3 class="text-lg font-medium text-gray-900 mb-4">
                            Associated Trade Pairs
                        </h3>
                        <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                            {#if firm.tradePairs && Array.isArray(firm.tradePairs.trade_pairs)}
                                {#each firm.tradePairs.trade_pairs.filter((pair: TradePairInfo) => pair.is_associated) as pair}
                                    <div class="bg-gray-50 rounded p-3">
                                        <p
                                            class="text-sm font-medium text-gray-900"
                                        >
                                            {pair.name}
                                        </p>
                                        {#if pair.current_label}
                                            <p class="text-xs text-gray-500">
                                                Label: {pair.current_label}
                                            </p>
                                        {/if}
                                    </div>
                                {/each}
                            {:else if firm.tradePairs && Array.isArray(firm.tradePairs)}
                                <p class="text-sm text-gray-500">
                                    No trade pairs associated
                                </p>
                            {:else}
                                <p class="text-sm text-gray-500">
                                    No trade pairs data available
                                </p>
                            {/if}
                        </div>
                    </div>

                    <!-- Recent Trades -->
                    <div class="px-6 py-4">
                        <h3 class="text-lg font-medium text-gray-900 mb-4">
                            Recent Trades
                        </h3>
                        {#if firm.trades.length > 0}
                            <div class="overflow-x-auto">
                                <table
                                    class="min-w-full divide-y divide-gray-200"
                                >
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
                                        {#each firm.trades as trade}
                                            <tr class="hover:bg-gray-50">
                                                <td
                                                    class="px-4 py-3 text-sm text-gray-900"
                                                    >{trade.id}</td
                                                >
                                                <td
                                                    class="px-4 py-3 text-sm text-gray-900"
                                                    >{trade.strategy}</td
                                                >
                                                <td class="px-4 py-3">
                                                    <span
                                                        class={`px-2 py-1 text-xs font-medium rounded-full ${trade.order_type === "buy" ? "bg-green-100 text-green-800" : "bg-red-100 text-red-800"}`}
                                                    >
                                                        {trade.order_type.toUpperCase()}
                                                    </span>
                                                </td>
                                                <td
                                                    class="px-4 py-3 text-sm text-gray-900"
                                                    >{trade.ticker}</td
                                                >
                                                <td
                                                    class="px-4 py-3 text-sm text-gray-900"
                                                    >{trade.contracts.toFixed(
                                                        3,
                                                    )}</td
                                                >
                                                <td
                                                    class="px-4 py-3 text-sm text-gray-900"
                                                    >${trade.position_size.toFixed(
                                                        2,
                                                    )}</td
                                                >
                                                <td
                                                    class="px-4 py-3 text-sm text-gray-900"
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
                </div>
            {/each}
        </div>
    </div>
</div>
