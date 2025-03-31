<script lang="ts">
    import type { TradePair } from "$lib/types/trade_pairs";
    import TradePairList from "$lib/components/TradePairList.svelte";
    import { BROWSER } from "esm-env";

    let { initialPairs = [] }: { initialPairs: TradePair[] } = $props();

    let pairs = $state<TradePair[]>(initialPairs);
    let newPairName = $state("");
    let error = $state<string | null>(null);
    let isLoading = $state(!initialPairs.length && BROWSER); // Only true on client if no initial data

    // Fetch pairs on client-side if not provided by SSR/load function
    if (BROWSER && !initialPairs.length) {
        $effect(() => {
            async function loadPairs() {
                isLoading = true;
                error = null;
                try {
                    const response = await fetch("/api/trade_pairs"); // Fetch from SvelteKit API route
                    if (!response.ok) {
                        throw new Error(
                            `Failed to fetch: ${response.statusText}`,
                        );
                    }
                    pairs = await response.json();
                } catch (err: any) {
                    console.error("Error loading pairs:", err);
                    error = err.message || "Could not load trade pairs.";
                } finally {
                    isLoading = false;
                }
            }
            loadPairs();
        });
    }

    async function addPair() {
        const nameToAdd = newPairName.trim();
        if (!nameToAdd) return;

        error = null;
        isLoading = true; // Indicate loading state

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
        // Optional: Add loading state for the specific row being saved

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
            // Update the pair in the local state
            pairs = pairs.map((p) => (p.id === id ? updatedPair : p));
        } catch (err: any) {
            console.error("Error saving pair:", err);
            error = err.message || "Could not save trade pair.";
            // Optional: Revert optimistic update if you implemented one
        } finally {
            // Optional: Remove loading state for the specific row
        }
    }

    async function handleDelete(idToDelete: number) {
        error = null;
        // Optional: Add loading state for the specific row being deleted

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

            // Remove the pair from the local state
            pairs = pairs.filter((p) => p.id !== idToDelete);
        } catch (err: any) {
            console.error("Error deleting pair:", err);
            error = err.message || "Could not delete trade pair.";
        } finally {
            // Optional: Remove loading state for the specific row
        }
    }
</script>

<!-- Basic Tailwind styling assumed -->
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
            {#if isLoading && !pairs.length}
                <!-- Show loading only on initial load or add -->
                Adding...
            {:else}
                Add Pair
            {/if}
        </button>
    </div>

    {#if isLoading && !pairs.length}
        <p class="text-center text-gray-500">Loading pairs...</p>
    {:else}
        <TradePairList bind:pairs onsave={handleSave} ondelete={handleDelete} />
    {/if}
</div>
