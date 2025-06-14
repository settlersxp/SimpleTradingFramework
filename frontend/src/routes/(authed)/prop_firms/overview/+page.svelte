<script lang="ts">
    import type { PropFirm } from "$lib/types/PropFirms";
    import PropFirmCard from "./PropFirmCard.svelte";

    const props = $props<{ data: { propFirms: PropFirm[] } }>();
    // Create a reactive state for prop firms
    let firms = $state<PropFirm[]>([...props.data.propFirms]);
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

            // Parse the response to get the updated firm data
            const result = await response.json();
            updateFirmInList(result, firmId);
        } catch (error) {
            console.error("Error syncing prop firm:", error);
            syncError =
                error instanceof Error ? error.message : "An error occurred";
        } finally {
            syncing = false;
        }
    }

    async function toggleStatus(firmId: number, status: boolean) {
        try {
            const response = await fetch(`/api/prop_firms/manage`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    action: status ? "add" : "remove",
                    propFirmId: firmId,
                }),
            });

            if (!response.ok) {
                throw new Error("Failed to toggle active");
            }

            // Update only the field is_active of the firm
            firms = firms.map((firm: PropFirm) =>
                firm.id === firmId ? { ...firm, is_active: status } : firm,
            );
        } catch (error) {
            console.error("Error toggling active:", error);
            syncError =
                error instanceof Error ? error.message : "An error occurred";
        }
    }

    // Function to update a firm in the list without reloading the page
    function updateFirmInList(result: any, firmId: number) {
        // Determine where the updated firm object is located in the response
        const updatedFirm: PropFirm | undefined = result?.prop_firm ?? result;
        console.log(updatedFirm);
        if (updatedFirm && typeof updatedFirm.id === "number") {
            // Replace only the matching firm in the array
            firms = firms.map((firm: PropFirm) =>
                firm.id === firmId ? updatedFirm : firm,
            );
        }
        // If the updated firm wasn't found, we silently ignore; no full reload.
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
                body: JSON.stringify({ prop_firm_id: null }),
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

    async function handleDeleteTradePair(firmId: number, pairId: number) {
        // Update only the targeted firm's tradePairs array, removing the deleted pair
        firms = firms.map((firm: PropFirm) => {
            if (firm.id === firmId) {
                return {
                    ...firm,
                    tradePairs: Array.isArray(firm.tradePairs)
                        ? firm.tradePairs.filter(
                              (pair: any) => pair.id !== pairId,
                          )
                        : firm.tradePairs,
                };
            }
            return firm;
        });
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
            {#each firms as firm}
                <PropFirmCard
                    {firm}
                    {syncing}
                    onSync={syncPropFirm}
                    onToggleStatus={toggleStatus}
                    onDelete={handleDeleteTradePair}
                />
            {/each}
        </div>
    </div>
</div>
