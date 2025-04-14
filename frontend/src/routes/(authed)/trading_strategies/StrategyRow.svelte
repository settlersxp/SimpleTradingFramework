<script lang="ts">
    import { enhance } from "$app/forms";
    import type { TradingStrategy } from "$lib/types/TradingStrategy";
    import { invalidateAll } from "$app/navigation";
    let { strategy }: { strategy: TradingStrategy } = $props();

    let editingStrategyId: number | null = $state(null);

    function startEditStrategy(strategy: TradingStrategy) {
        editingStrategyId = strategy.id;
    }

    function cancelEdit() {
        editingStrategyId = null;
    }

    function handleDelete(strategyId: number) {
        if (confirm("Are you sure you want to delete this trading strategy?")) {
            // Find the form associated with this delete button and submit it
            const formElement = document.getElementById(
                `delete-form-${strategyId}`,
            ) as HTMLFormElement;
            if (formElement) {
                formElement.requestSubmit();
            }
        }
    }

    function handleSuccess() {
        editingStrategyId = null; // Close edit form on success
        invalidateAll(); // Re-run load function to refresh data
        // Clear potential form errors from previous submissions
        // form = null; // No longer needed to manually clear, SvelteKit handles it with enhance
    }
</script>

{#if editingStrategyId === strategy.id}
    <tr class="bg-blue-50">
        <td class="border px-4 py-2" colspan="4">
            <form
                method="POST"
                action="?/update"
                use:enhance={() => {
                    return async ({ result }) => {
                        if (result.type === "success") {
                            handleSuccess();
                        }
                    };
                }}
            >
                <input type="hidden" name="id" value={strategy.id} />
                <div class="flex flex-wrap -mx-2 items-center">
                    <div class="px-2 w-1/3 mb-2 md:mb-0">
                        <input
                            class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                            type="text"
                            name="name"
                            placeholder="Strategy name"
                            value={strategy.name}
                            required
                        />
                    </div>
                    <div class="px-2 w-1/3 mb-2 md:mb-0">
                        <input
                            class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                            type="text"
                            name="description"
                            placeholder="Description (optional)"
                            value={strategy.description || ""}
                        />
                    </div>
                    <div class="px-2 w-1/3 flex">
                        <button
                            type="submit"
                            class="bg-green-500 hover:bg-green-700 text-white font-bold py-1 px-2 rounded mr-2 focus:outline-none focus:shadow-outline"
                        >
                            Save
                        </button>
                        <button
                            type="button"
                            onclick={cancelEdit}
                            class="bg-gray-500 hover:bg-gray-700 text-white font-bold py-1 px-2 rounded focus:outline-none focus:shadow-outline"
                        >
                            Cancel
                        </button>
                    </div>
                </div>
            </form>
        </td>
    </tr>
{:else}
    <tr>
        <td class="border px-4 py-2">{strategy.name}</td>
        <td class="border px-4 py-2">{strategy.description || "-"}</td>
        <td class="border px-4 py-2"
            >{new Date(strategy.created_at).toLocaleDateString()}</td
        >
        <td class="border px-4 py-2">
            <button
                onclick={() => startEditStrategy(strategy)}
                class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-1 px-2 rounded mr-2 focus:outline-none focus:shadow-outline"
            >
                Edit
            </button>

            <!-- Delete Form -->
            <form
                method="POST"
                action="?/delete"
                use:enhance={() => {
                    return async ({ result }) => {
                        if (result.type === "success") {
                            handleSuccess();
                        }
                    };
                }}
                class="inline-block"
                id={`delete-form-${strategy.id}`}
            >
                <input type="hidden" name="id" value={strategy.id} />
                <button
                    type="button"
                    onclick={() => handleDelete(strategy.id)}
                    class="bg-red-500 hover:bg-red-700 text-white font-bold py-1 px-2 rounded focus:outline-none focus:shadow-outline"
                >
                    Delete
                </button>
            </form>
        </td>
    </tr>
{/if}
