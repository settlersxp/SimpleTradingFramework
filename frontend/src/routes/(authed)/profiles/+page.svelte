<script lang="ts">
    import { user } from "$lib/stores/auth";
    import { deleteUser } from "$lib/api/auth";
    import { goto } from "$app/navigation";
    import AuthGuard from "$lib/components/AuthGuard.svelte";

    let isDeleting = false;
    let showDeleteConfirm = false;
    let error = "";

    async function handleDeleteAccount() {
        if (!$user) return;

        isDeleting = true;
        error = "";

        try {
            const response = await deleteUser($user.id);

            if (response.error) {
                error = response.error;
            } else {
                goto("/login");
            }
        } catch (err) {
            error = "An unexpected error occurred";
        } finally {
            isDeleting = false;
            showDeleteConfirm = false;
        }
    }
</script>

<AuthGuard>
    <div class="py-10">
        <header>
            <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <h1 class="text-3xl font-bold leading-tight text-gray-900">
                    Profile
                </h1>
            </div>
        </header>
        <main>
            <div class="max-w-7xl mx-auto sm:px-6 lg:px-8">
                <div class="px-4 py-8 sm:px-0">
                    <div class="bg-white shadow overflow-hidden sm:rounded-lg">
                        <div class="px-4 py-5 sm:px-6">
                            <h3
                                class="text-lg leading-6 font-medium text-gray-900"
                            >
                                User Information
                            </h3>
                            <p class="mt-1 max-w-2xl text-sm text-gray-500">
                                Personal details and account settings.
                            </p>
                        </div>
                        <div class="border-t border-gray-200">
                            <dl>
                                <div
                                    class="bg-gray-50 px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6"
                                >
                                    <dt
                                        class="text-sm font-medium text-gray-500"
                                    >
                                        Email address
                                    </dt>
                                    <dd
                                        class="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2"
                                    >
                                        {$user?.email}
                                    </dd>
                                </div>
                                <div
                                    class="bg-white px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6"
                                >
                                    <dt
                                        class="text-sm font-medium text-gray-500"
                                    >
                                        Account created
                                    </dt>
                                    <dd
                                        class="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2"
                                    >
                                        {new Date(
                                            $user?.created_at || "",
                                        ).toLocaleString()}
                                    </dd>
                                </div>
                                <div
                                    class="bg-gray-50 px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6"
                                >
                                    <dt
                                        class="text-sm font-medium text-gray-500"
                                    >
                                        Last updated
                                    </dt>
                                    <dd
                                        class="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2"
                                    >
                                        {new Date(
                                            $user?.updated_at || "",
                                        ).toLocaleString()}
                                    </dd>
                                </div>
                                <div
                                    class="bg-white px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6"
                                >
                                    <dt
                                        class="text-sm font-medium text-gray-500"
                                    >
                                        Active prop firms
                                    </dt>
                                    <dd
                                        class="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2"
                                    >
                                        {$user?.prop_firms.length || 0}
                                    </dd>
                                </div>
                            </dl>
                        </div>
                    </div>

                    <div class="mt-10">
                        <h3
                            class="text-lg leading-6 font-medium text-gray-900 mb-4"
                        >
                            Danger Zone
                        </h3>

                        {#if error}
                            <div class="rounded-md bg-red-50 p-4 mb-4">
                                <div class="flex">
                                    <div class="ml-3">
                                        <h3
                                            class="text-sm font-medium text-red-800"
                                        >
                                            {error}
                                        </h3>
                                    </div>
                                </div>
                            </div>
                        {/if}

                        {#if showDeleteConfirm}
                            <div
                                class="bg-red-50 border-l-4 border-red-400 p-4 mb-4"
                            >
                                <div class="flex">
                                    <div class="ml-3">
                                        <p class="text-sm text-red-700">
                                            Are you sure you want to delete your
                                            account? This action cannot be
                                            undone.
                                        </p>
                                        <div class="mt-4 flex space-x-4">
                                            <button
                                                onclick={() =>
                                                    (showDeleteConfirm = false)}
                                                class="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                                            >
                                                Cancel
                                            </button>
                                            <button
                                                onclick={handleDeleteAccount}
                                                disabled={isDeleting}
                                                class="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 disabled:opacity-50"
                                            >
                                                {#if isDeleting}
                                                    <svg
                                                        class="animate-spin -ml-1 mr-2 h-4 w-4 text-white"
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
                                                    Deleting...
                                                {:else}
                                                    Confirm Delete
                                                {/if}
                                            </button>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        {:else}
                            <button
                                onclick={() => (showDeleteConfirm = true)}
                                class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
                            >
                                Delete Account
                            </button>
                        {/if}
                    </div>
                </div>
            </div>
        </main>
    </div>
</AuthGuard>
