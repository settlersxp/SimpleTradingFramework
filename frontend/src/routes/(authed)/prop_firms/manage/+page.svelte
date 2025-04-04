<script lang="ts">
    // Removed onMount and direct API imports for initial load
    import type { PropFirm } from "../../../../lib/types/PropFirms";

    let { data } = $props(); // Get data from +page.ts load function

    // Use $state for reactive variables
    let userPropFirms = $state<PropFirm[]>(data.userPropFirms || []);
    let allPropFirms = $state<PropFirm[]>(data.allPropFirms || []);
    let isLoading = $state(false); // For actions, initial load handled by SvelteKit
    let initialError = $state(data.error || ""); // Error from initial load
    let actionError = $state(""); // Error from add/remove actions
    let successMessage = $state("");

    // $derived state for checking active status reactively
    const userPropFirmIds = $derived(new Set(userPropFirms.map((pf) => pf.id)));

    function isActive(propFirm: PropFirm): boolean {
        return userPropFirmIds.has(propFirm.id);
    }

    async function togglePropFirm(propFirm: PropFirm) {
        actionError = "";
        successMessage = "";
        isLoading = true;
        const currentlyActive = isActive(propFirm);
        const action = currentlyActive ? "remove" : "add";

        try {
            const response = await fetch("/api/prop_firms/manage", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    action: action,
                    propFirmId: propFirm.id,
                }),
            });

            const result = await response.json();

            if (!response.ok) {
                actionError =
                    result.message ||
                    `Failed to ${action} prop firm. Status: ${response.status}`;
            } else {
                successMessage =
                    result.message ||
                    `${action === "add" ? "Added" : "Removed"} ${propFirm.name} successfully`;
                // Update local state directly for instant UI feedback
                if (action === "add") {
                    userPropFirms.push(propFirm);
                    // Ensure reactivity by reassigning (though push might trigger in Svelte 5)
                    userPropFirms = userPropFirms;
                } else {
                    userPropFirms = userPropFirms.filter(
                        (pf) => pf.id !== propFirm.id,
                    );
                }
            }
        } catch (err: any) {
            actionError =
                err.message ||
                "An unexpected error occurred during the action.";
            console.error(err);
        } finally {
            isLoading = false;
        }
    }

    // No loadData function needed anymore
</script>

<header>
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <h1 class="text-3xl font-bold leading-tight text-gray-900">
            Manage Prop Firms
        </h1>
    </div>
</header>
<main>
    <div class="max-w-7xl mx-auto sm:px-6 lg:px-8">
        <div class="px-4 py-8 sm:px-0">
            {#if initialError}
                <div class="rounded-md bg-red-50 p-4 mb-6">
                    <div class="flex">
                        <div class="ml-3">
                            <h3 class="text-sm font-medium text-red-800">
                                Error loading data: {initialError}
                            </h3>
                        </div>
                    </div>
                </div>
            {/if}
            {#if actionError}
                <div class="rounded-md bg-red-50 p-4 mb-6">
                    <div class="flex">
                        <div class="ml-3">
                            <h3 class="text-sm font-medium text-red-800">
                                {actionError}
                            </h3>
                        </div>
                    </div>
                </div>
            {/if}

            {#if successMessage}
                <div class="rounded-md bg-green-50 p-4 mb-6">
                    <div class="flex">
                        <div class="ml-3">
                            <h3 class="text-sm font-medium text-green-800">
                                {successMessage}
                            </h3>
                        </div>
                    </div>
                </div>
            {/if}

            {#if !initialError}
                <div class="bg-white shadow overflow-hidden sm:rounded-md">
                    <ul class="divide-y divide-gray-200">
                        {#each allPropFirms as propFirm (propFirm.id)}
                            <li>
                                <div class="px-4 py-4 sm:px-6">
                                    <div
                                        class="flex items-center justify-between"
                                    >
                                        <div class="flex items-center">
                                            <p
                                                class="text-sm font-medium text-indigo-600 truncate"
                                            >
                                                {propFirm.name}
                                            </p>
                                        </div>
                                        <div class="ml-2 flex-shrink-0 flex">
                                            <button
                                                onclick={() =>
                                                    togglePropFirm(propFirm)}
                                                disabled={isLoading}
                                                class={`px-3 py-1 rounded-md text-sm font-medium ${
                                                    isActive(propFirm)
                                                        ? "bg-green-100 text-green-800 hover:bg-green-200"
                                                        : "bg-gray-100 text-gray-800 hover:bg-gray-200"
                                                } ${isLoading ? "opacity-50 cursor-not-allowed" : ""}`}
                                            >
                                                {#if isLoading && isActive(propFirm)}
                                                    Removing...
                                                {:else if isLoading && !isActive(propFirm)}
                                                    Adding...
                                                {:else if isActive(propFirm)}
                                                    Active
                                                {:else}
                                                    Inactive
                                                {/if}
                                            </button>
                                        </div>
                                    </div>
                                    <div
                                        class="mt-2 sm:flex sm:justify-between"
                                    >
                                        <div class="sm:flex">
                                            <p
                                                class="flex items-center text-sm text-gray-500"
                                            >
                                                Platform: {propFirm.platform_type ??
                                                    "N/A"}
                                            </p>
                                            <p
                                                class="mt-2 flex items-center text-sm text-gray-500 sm:mt-0 sm:ml-6"
                                            >
                                                Balance: ${propFirm.full_balance?.toFixed(
                                                    2,
                                                ) ?? "N/A"}
                                            </p>
                                        </div>
                                    </div>
                                </div>
                            </li>
                        {/each}

                        {#if allPropFirms.length === 0}
                            <li>
                                <div
                                    class="px-4 py-8 text-center text-gray-500"
                                >
                                    No prop firms available. Create one first.
                                </div>
                            </li>
                        {/if}
                    </ul>
                </div>

                <div class="mt-6 flex justify-end">
                    <a
                        href="/prop_firms/register"
                        class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                    >
                        Create New Prop Firm
                    </a>
                </div>
            {/if}
            {#if isLoading && !initialError}
                <div
                    class="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center z-50"
                >
                    <div
                        class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-white"
                    ></div>
                </div>
            {/if}
        </div>
    </div>
</main>
