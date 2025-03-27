<script lang="ts">
    import type { TradePair } from "$lib/types/trade_pairs";

    type SaveEvent = { id: number; name: string };
    type DeleteEvent = number;

    let {
        pairs = $bindable([]),
        onsave,
        ondelete,
    }: {
        pairs: TradePair[];
        onsave?: (detail: SaveEvent) => void;
        ondelete?: (detail: DeleteEvent) => void;
    } = $props();

    let editingId = $state<number | null>(null);
    let editValue = $state("");

    function startEdit(pair: TradePair) {
        editingId = pair.id;
        editValue = pair.name;
        // Ensure focus happens after the input is rendered
        setTimeout(() => {
            const input = document.querySelector<HTMLInputElement>(
                `tr[data-id="${pair.id}"] .edit-input`,
            );
            input?.focus();
            input?.select();
        }, 0);
    }

    function cancelEdit() {
        editingId = null;
        editValue = "";
    }

    function saveEdit(id: number) {
        if (!editValue.trim()) return; // Prevent saving empty names
        onsave?.({ id, name: editValue.trim() });
        // Optimistically update UI or wait for parent confirmation?
        // For simplicity, we'll let the parent handle the state update after successful save.
        cancelEdit(); // Exit edit mode immediately
    }

    function handleDelete(id: number) {
        if (confirm("Are you sure you want to delete this pair?")) {
            ondelete?.(id);
        }
    }

    // Handle Enter key press in edit input
    function handleKeydown(event: KeyboardEvent, id: number) {
        if (event.key === "Enter") {
            saveEdit(id);
        } else if (event.key === "Escape") {
            cancelEdit();
        }
    }
</script>

<!-- Basic Tailwind styling assumed, add your specific classes -->
<div class="overflow-x-auto">
    <table class="min-w-full bg-white border border-gray-200">
        <thead>
            <tr class="bg-gray-100">
                <th
                    class="px-4 py-2 border-b text-left text-sm font-medium text-gray-600"
                    >ID</th
                >
                <th
                    class="px-4 py-2 border-b text-left text-sm font-medium text-gray-600"
                    >Name</th
                >
                <th
                    class="px-4 py-2 border-b text-left text-sm font-medium text-gray-600"
                    >Created At</th
                >
                <th
                    class="px-4 py-2 border-b text-left text-sm font-medium text-gray-600"
                    >Actions</th
                >
            </tr>
        </thead>
        <tbody>
            {#if pairs.length === 0}
                <tr>
                    <td
                        colspan="4"
                        class="px-4 py-3 border-b text-center text-gray-500"
                        >No trade pairs found.</td
                    >
                </tr>
            {/if}
            {#each pairs as pair (pair.id)}
                <tr data-id={pair.id} class="hover:bg-gray-50">
                    <td class="px-4 py-2 border-b text-sm text-gray-700"
                        >{pair.id}</td
                    >
                    <td class="px-4 py-2 border-b text-sm text-gray-700">
                        {#if editingId === pair.id}
                            <input
                                type="text"
                                bind:value={editValue}
                                onkeydown={(e) => handleKeydown(e, pair.id)}
                                onblur={() => saveEdit(pair.id)}
                                class="edit-input border rounded px-2 py-1 w-full"
                            />
                        {:else}
                            <span class="pair-name">{pair.name}</span>
                        {/if}
                    </td>
                    <td class="px-4 py-2 border-b text-sm text-gray-700">
                        {new Date(pair.created_at).toLocaleString()}
                    </td>
                    <td class="px-4 py-2 border-b text-sm">
                        <div class="flex gap-2">
                            {#if editingId === pair.id}
                                <button
                                    onclick={() => saveEdit(pair.id)}
                                    class="px-3 py-1 bg-green-500 text-white rounded hover:bg-green-600 text-xs"
                                >
                                    Save
                                </button>
                                <button
                                    onclick={cancelEdit}
                                    class="px-3 py-1 bg-gray-500 text-white rounded hover:bg-gray-600 text-xs"
                                >
                                    Cancel
                                </button>
                            {:else}
                                <button
                                    onclick={() => startEdit(pair)}
                                    class="px-3 py-1 bg-blue-500 text-white rounded hover:bg-blue-600 text-xs"
                                >
                                    Edit
                                </button>
                                <button
                                    onclick={() => handleDelete(pair.id)}
                                    class="px-3 py-1 bg-red-500 text-white rounded hover:bg-red-600 text-xs"
                                >
                                    Delete
                                </button>
                            {/if}
                        </div>
                    </td>
                </tr>
            {/each}
        </tbody>
    </table>
</div>
