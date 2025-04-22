<script lang="ts">
    import { onMount } from "svelte";
    import { goto } from "$app/navigation";
    import { page } from "$app/state";

    // Get the id from the page store params
    const id = page.params.id;

    type PropFirm = {
        id: number;
        name: string;
        full_balance: number;
        available_balance: number;
        drawdown_percentage: number;
        is_active: boolean;
        username: string;
        password: string;
        ip_address: string;
        port: number;
        platform_type: string;
    };

    let propFirm = $state<PropFirm | null>(null);
    let loading = $state(true);
    let error = $state<string | null>(null);
    let isSubmitting = $state(false);

    onMount(() => {
        fetchPropFirm();
    });

    async function fetchPropFirm() {
        try {
            console.log("Fetching prop firm:", id);
            const response = await fetch(`/api/prop_firms/${id}`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            propFirm = await response.json();
        } catch (e) {
            error = e instanceof Error ? e.message : "An error occurred";
            console.error("Error fetching prop firm:", e);
        } finally {
            loading = false;
        }
    }

    async function handleSubmit() {
        if (!propFirm) return;

        isSubmitting = true;
        error = null;

        try {
            const response = await fetch(`/api/prop_firms/${id}`, {
                method: "PUT",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(propFirm),
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(
                    errorData.error || `HTTP error! status: ${response.status}`,
                );
            }

            await goto("/prop_firms/overview");
        } catch (e) {
            error = e instanceof Error ? e.message : "An error occurred";
            console.error("Error updating prop firm:", e);
        } finally {
            isSubmitting = false;
        }
    }
</script>

<div class="min-h-screen bg-gray-100 p-8">
    <div class="max-w-3xl mx-auto">
        <div class="bg-white rounded-lg shadow-sm">
            <div class="px-6 py-4 border-b border-gray-200">
                <h2 class="text-xl font-semibold text-gray-800">
                    {#if propFirm}
                        Edit Prop Firm: {propFirm.name}
                    {:else}
                        Edit Prop Firm
                    {/if}
                </h2>
            </div>

            {#if loading}
                <div class="flex justify-center items-center p-8">
                    <div
                        class="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-500"
                    ></div>
                </div>
            {:else if error}
                <div
                    class="p-4 bg-red-100 text-red-700 border-l-4 border-red-500"
                >
                    <p>{error}</p>
                </div>
            {:else if propFirm}
                <form onsubmit={handleSubmit} class="px-6 py-6 space-y-6">
                    <!-- Name Field -->
                    <div>
                        <label
                            for="name"
                            class="block text-sm font-medium text-gray-700"
                            >Name</label
                        >
                        <input
                            type="text"
                            id="name"
                            bind:value={propFirm.name}
                            class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                            required
                        />
                    </div>

                    <!-- Username & Password -->
                    <div class="grid grid-cols-1 gap-6 sm:grid-cols-2">
                        <div>
                            <label
                                for="username"
                                class="block text-sm font-medium text-gray-700"
                                >Username</label
                            >
                            <input
                                type="text"
                                id="username"
                                bind:value={propFirm.username}
                                class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                            />
                        </div>
                        <div>
                            <label
                                for="password"
                                class="block text-sm font-medium text-gray-700"
                                >Password</label
                            >
                            <input
                                type="password"
                                id="password"
                                bind:value={propFirm.password}
                                class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                            />
                        </div>
                    </div>

                    <!-- Connection Details -->
                    <div class="grid grid-cols-1 gap-6 sm:grid-cols-3">
                        <div>
                            <label
                                for="ip_address"
                                class="block text-sm font-medium text-gray-700"
                                >IP Address</label
                            >
                            <input
                                type="text"
                                id="ip_address"
                                bind:value={propFirm.ip_address}
                                class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                            />
                        </div>
                        <div>
                            <label
                                for="port"
                                class="block text-sm font-medium text-gray-700"
                                >Port</label
                            >
                            <input
                                type="number"
                                id="port"
                                bind:value={propFirm.port}
                                class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                            />
                        </div>
                        <div>
                            <label
                                for="platform_type"
                                class="block text-sm font-medium text-gray-700"
                                >Platform Type</label
                            >
                            <select
                                id="platform_type"
                                bind:value={propFirm.platform_type}
                                class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                            >
                                <option value="MT4">MT4</option>
                                <option value="MT5">MT5</option>
                                <option value="cTrader">cTrader</option>
                            </select>
                        </div>
                    </div>

                    <!-- Balance Information -->
                    <div class="grid grid-cols-1 gap-6 sm:grid-cols-3">
                        <div>
                            <label
                                for="full_balance"
                                class="block text-sm font-medium text-gray-700"
                                >Full Balance</label
                            >
                            <input
                                type="number"
                                id="full_balance"
                                bind:value={propFirm.full_balance}
                                step="0.01"
                                class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                            />
                        </div>
                        <div>
                            <label
                                for="available_balance"
                                class="block text-sm font-medium text-gray-700"
                                >Available Balance</label
                            >
                            <input
                                type="number"
                                id="available_balance"
                                bind:value={propFirm.available_balance}
                                step="0.01"
                                class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                            />
                        </div>
                        <div>
                            <label
                                for="drawdown_percentage"
                                class="block text-sm font-medium text-gray-700"
                                >Drawdown Percentage</label
                            >
                            <input
                                type="number"
                                id="drawdown_percentage"
                                bind:value={propFirm.drawdown_percentage}
                                step="0.01"
                                class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                            />
                        </div>
                    </div>

                    <!-- Active Status -->
                    <div class="flex items-center">
                        <input
                            type="checkbox"
                            id="is_active"
                            bind:checked={propFirm.is_active}
                            class="h-4 w-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
                        />
                        <label
                            for="is_active"
                            class="ml-2 block text-sm text-gray-700"
                            >Active</label
                        >
                    </div>

                    <!-- Form Actions -->
                    <div class="flex justify-end space-x-4 pt-4">
                        <a
                            href="/prop_firms/overview"
                            class="inline-flex justify-center rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
                        >
                            Cancel
                        </a>
                        <a
                            href={`/prop_firms/${id}/trade_pairs`}
                            class="inline-flex justify-center rounded-md border border-transparent bg-blue-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                        >
                            Associate Trade Pairs
                        </a>
                        <button
                            type="submit"
                            disabled={isSubmitting}
                            class="inline-flex justify-center rounded-md border border-transparent bg-indigo-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            {#if isSubmitting}
                                <svg
                                    class="animate-spin -ml-1 mr-3 h-5 w-5 text-white"
                                    xmlns="http://www.w3.org/2000/svg"
                                    fill="none"
                                    viewBox="0 0 24 24"
                                >
                                    <circle
                                        class="opacity-25"
                                        cx="12"
                                        cy="12"
                                        r="10"
                                        stroke="currentColor"
                                        stroke-width="4"
                                    ></circle>
                                    <path
                                        class="opacity-75"
                                        fill="currentColor"
                                        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                                    ></path>
                                </svg>
                                Updating...
                            {:else}
                                Update Prop Firm
                            {/if}
                        </button>
                    </div>
                </form>
            {/if}
        </div>
    </div>
</div>
