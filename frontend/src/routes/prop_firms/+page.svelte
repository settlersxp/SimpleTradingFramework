<script lang="ts">
    import { goto } from "$app/navigation";

    type PropFirmForm = {
        name: string;
        username: string;
        password: string;
        ip_address: string;
        port: number;
        platform_type: string;
        is_active: boolean;
        full_balance: number;
        available_balance: number;
        dowdown_percentage: number;
    };

    let form: PropFirmForm = {
        name: "",
        username: "",
        password: "",
        ip_address: "127.0.0.1",
        port: 8080,
        platform_type: "MT5",
        is_active: true,
        full_balance: 0,
        available_balance: 0,
        dowdown_percentage: 0,
    };

    let isSubmitting = false;
    let error: string | null = null;

    async function handleSubmit() {
        isSubmitting = true;
        error = null;

        try {
            const response = await fetch("/api/prop_firms", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(form),
            });

            if (!response.ok) {
                throw new Error("Failed to create prop firm");
            }

            await goto("/prop_firms");
        } catch (err) {
            console.error("Error creating prop firm:", err);
            error = err instanceof Error ? err.message : "An error occurred";
        } finally {
            isSubmitting = false;
        }
    }
</script>

<div class="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-3xl mx-auto">
        <div class="bg-white shadow-lg rounded-lg">
            <!-- Header -->
            <div class="px-6 py-4 border-b border-gray-200">
                <h2 class="text-2xl font-semibold text-gray-800">
                    Create New Prop Firm
                </h2>
            </div>

            <!-- Form -->
            <form
                on:submit|preventDefault={handleSubmit}
                class="px-6 py-6 space-y-6"
            >
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
                        bind:value={form.name}
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
                            bind:value={form.username}
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
                            bind:value={form.password}
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
                            bind:value={form.ip_address}
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
                            bind:value={form.port}
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
                            bind:value={form.platform_type}
                            class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                        >
                            <option value="MT4">MT4</option>
                            <option value="MT5">MT5</option>
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
                            bind:value={form.full_balance}
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
                            bind:value={form.available_balance}
                            step="0.01"
                            class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                        />
                    </div>
                    <div>
                        <label
                            for="dowdown_percentage"
                            class="block text-sm font-medium text-gray-700"
                            >Drawdown Percentage</label
                        >
                        <input
                            type="number"
                            id="dowdown_percentage"
                            bind:value={form.dowdown_percentage}
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
                        bind:checked={form.is_active}
                        class="h-4 w-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
                    />
                    <label
                        for="is_active"
                        class="ml-2 block text-sm text-gray-700">Active</label
                    >
                </div>

                <!-- Form Actions -->
                <div class="flex flex-col space-y-4">
                    {#if error}
                        <div class="bg-red-50 border-l-4 border-red-400 p-4">
                            <div class="flex">
                                <div class="flex-shrink-0">
                                    <!-- You can add an error icon here if you want -->
                                </div>
                                <div class="ml-3">
                                    <p class="text-sm text-red-700">
                                        {error}
                                    </p>
                                </div>
                            </div>
                        </div>
                    {/if}

                    <div class="flex justify-end space-x-4 pt-4">
                        <a
                            href="/prop_firms"
                            class="inline-flex justify-center rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
                        >
                            Cancel
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
                                Creating...
                            {:else}
                                Create Prop Firm
                            {/if}
                        </button>
                    </div>
                </div>
            </form>
        </div>
    </div>
</div>

<style>
    /* Add any additional custom styles here if needed */
</style>
