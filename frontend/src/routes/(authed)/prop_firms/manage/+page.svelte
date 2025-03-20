<script lang="ts">
    import { onMount } from "svelte";

    import {
        getUserPropFirms,
        addPropFirmToUser,
        removePropFirmFromUser,
    } from "$lib/api/user_prop_firms";
    import type { PropFirm } from "$lib/api/prop_firms";
    import { getAllPropFirms } from "$lib/api/prop_firms";
    let userPropFirms: PropFirm[] = [];
    let allPropFirms: PropFirm[] = [];
    let isLoading = true;
    let error = "";
    let successMessage = "";

    onMount(async () => {
        await loadData();
    });

    async function loadData() {
        isLoading = true;
        error = "";
        successMessage = "";

        try {
            // Load user's prop firms
            const userResponse = await getUserPropFirms();
            if (userResponse.error) {
                error = userResponse.error;
            } else {
                userPropFirms = userResponse.prop_firms || [];
            }

            // Load all prop firms
            const allResponse = await getAllPropFirms();
            if (allResponse.error) {
                error = allResponse.error;
            } else {
                allPropFirms = allResponse.prop_firms || [];
            }
        } catch (err) {
            error = "Failed to load prop firms";
        } finally {
            isLoading = false;
        }
    }

    function isActive(propFirm: PropFirm): boolean {
        return userPropFirms.some((pf) => pf.id === propFirm.id);
    }

    async function togglePropFirm(propFirm: PropFirm) {
        error = "";
        successMessage = "";
        isLoading = true;

        try {
            if (isActive(propFirm)) {
                // Remove prop firm
                const response = await removePropFirmFromUser(propFirm.id);
                if (response.error) {
                    error = response.error;
                } else {
                    successMessage = `Removed ${propFirm.name} from your active prop firms`;
                }
            } else {
                // Add prop firm
                const response = await addPropFirmToUser(propFirm.id);
                if (response.error) {
                    error = response.error;
                } else {
                    successMessage = `Added ${propFirm.name} to your active prop firms`;
                }
            }

            // Reload data
            await loadData();
        } catch (err) {
            error = "An unexpected error occurred";
        } finally {
            isLoading = false;
        }
    }
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
            {#if error}
                <div class="rounded-md bg-red-50 p-4 mb-6">
                    <div class="flex">
                        <div class="ml-3">
                            <h3 class="text-sm font-medium text-red-800">
                                {error}
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

            {#if isLoading}
                <div class="flex justify-center py-12">
                    <div
                        class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-indigo-500"
                    ></div>
                </div>
            {:else}
                <div class="bg-white shadow overflow-hidden sm:rounded-md">
                    <ul class="divide-y divide-gray-200">
                        {#each allPropFirms as propFirm}
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
                                                class={`px-3 py-1 rounded-md text-sm font-medium ${
                                                    isActive(propFirm)
                                                        ? "bg-green-100 text-green-800 hover:bg-green-200"
                                                        : "bg-gray-100 text-gray-800 hover:bg-gray-200"
                                                }`}
                                            >
                                                {isActive(propFirm)
                                                    ? "Active"
                                                    : "Inactive"}
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
                                                Platform: {propFirm.platform_type}
                                            </p>
                                            <p
                                                class="mt-2 flex items-center text-sm text-gray-500 sm:mt-0 sm:ml-6"
                                            >
                                                Balance: ${propFirm.full_balance.toFixed(
                                                    2,
                                                )}
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
                        href="/prop_firms/create"
                        class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                    >
                        Create New Prop Firm
                    </a>
                </div>
            {/if}
        </div>
    </div>
</main>
