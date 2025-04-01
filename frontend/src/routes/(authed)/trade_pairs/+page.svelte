<script lang="ts">
    // Removed TradePairComponentManager import
    import type { PageData } from "./$types";
    import type { TradePair } from "$lib/types/trade_pairs";
    import TradePairList from "$lib/components/TradePairList.svelte";

    let { data }: { data: PageData } = $props();

    // State moved from TradePairComponentManager
    let pairs = $state<TradePair[]>(data.pairs ?? []);
    let newPairName = $state("");
    let error = $state<string | null>(data.error ?? null); // Initialize error from load function too
    let isLoading = $state(false); // Initial load handled by SvelteKit, only track mutations

    // --- CRUD Functions moved from TradePairComponentManager ---

    async function addPair() {
        const nameToAdd = newPairName.trim();
        if (!nameToAdd) return;

        error = null;
        isLoading = true; // Indicate loading state for add operation

        try {
            const response = await fetch("/api/trade_pairs", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ name: nameToAdd }),
            });

            if (!response.ok) {
                const errData = await response.json().catch(() => ({}));
                throw new Error(
                    errData.message ||
                        `Failed to add pair: ${response.statusText}`,
                );
            }

            const newPair: TradePair = await response.json();
            pairs = [...pairs, newPair]; // Add to the list
            newPairName = ""; // Clear input
        } catch (err: any) {
            console.error("Error adding pair:", err);
            error = err.message || "Could not add trade pair.";
        } finally {
            isLoading = false;
        }
    }

    async function handleSave({ id, name }: { id: number; name: string }) {
        error = null;
        // Consider adding per-row loading state if needed
        // isLoading = true; // Maybe set loading state here

        try {
            const response = await fetch("/api/trade_pairs", {
                method: "PUT",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ id, name }),
            });

            if (!response.ok) {
                const errData = await response.json().catch(() => ({}));
                throw new Error(
                    errData.message ||
                        `Failed to save pair: ${response.statusText}`,
                );
            }

            const updatedPair: TradePair = await response.json();
            pairs = pairs.map((p) => (p.id === id ? updatedPair : p));
        } catch (err: any) {
            console.error("Error saving pair:", err);
            error = err.message || "Could not save trade pair.";
        } finally {
            // isLoading = false; // Reset loading state if set
        }
    }

    async function handleDelete(idToDelete: number) {
        error = null;
        // Consider adding per-row loading state if needed
        // isLoading = true; // Maybe set loading state here

        try {
            const response = await fetch("/api/trade_pairs", {
                method: "DELETE",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ id: idToDelete }),
            });

            if (!response.ok) {
                const errData = await response.json().catch(() => ({}));
                throw new Error(
                    errData.message ||
                        `Failed to delete pair: ${response.statusText}`,
                );
            }

            pairs = pairs.filter((p) => p.id !== idToDelete);
        } catch (err: any) {
            console.error("Error deleting pair:", err);
            error = err.message || "Could not delete trade pair.";
        } finally {
            // isLoading = false; // Reset loading state if set
        }
    }
</script>

<!-- Markup moved from TradePairComponentManager -->
<div class="p-4 space-y-4">
    <h1 class="text-2xl font-bold">Trade Pairs Management</h1>

    {#if error}
        <div class="p-3 bg-red-100 text-red-700 border border-red-300 rounded">
            Error: {error}
        </div>
    {/if}

    <div class="add-form flex gap-2 items-center p-4 bg-gray-50 border rounded">
        <input
            type="text"
            bind:value={newPairName}
            placeholder="Enter pair (e.g., BTCUSD.T)"
            class="border rounded px-3 py-2 flex-grow focus:outline-none focus:ring-2 focus:ring-blue-500"
            disabled={isLoading}
            onkeydown={(e) => e.key === "Enter" && addPair()}
        />
        <button
            onclick={addPair}
            class="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600 disabled:opacity-50"
            disabled={isLoading || !newPairName.trim()}
        >
            {#if isLoading}
                <!-- Simplified loading state for add -->
                Adding...
            {:else}
                Add Pair
            {/if}
        </button>
    </div>

    <!-- Render TradePairList directly -->
    <TradePairList bind:pairs onsave={handleSave} ondelete={handleDelete} />

    <!-- Removed loading indicator for initial load, handled by SvelteKit -->
</div>
