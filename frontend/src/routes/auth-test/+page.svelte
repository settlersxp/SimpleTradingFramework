<script lang="ts">
    import { onMount } from "svelte";
    import { user, isAuthenticated, isLoading } from "$lib/stores/auth";
    import { getCurrentUser } from "$lib/api/auth";

    let testResponse = $state<any>(null);
    let testError = $state<string | null>(null);
    let testLoading = $state(false);

    async function testAuthEndpoint() {
        testLoading = true;
        testError = null;

        try {
            const response = await getCurrentUser();
            testResponse = response;
        } catch (error) {
            testError =
                error instanceof Error ? error.message : "Unknown error";
        } finally {
            testLoading = false;
        }
    }
</script>

<div class="min-h-screen bg-gray-100 p-8">
    <div class="max-w-3xl mx-auto">
        <div class="bg-white rounded-lg shadow-sm p-6">
            <h1 class="text-2xl font-bold mb-6">Auth Test Page</h1>

            <div class="mb-6">
                <h2 class="text-xl font-semibold mb-2">Auth Store Status</h2>
                <div class="bg-gray-100 p-4 rounded">
                    <p><strong>Loading:</strong> {$isLoading ? "Yes" : "No"}</p>
                    <p>
                        <strong>Authenticated:</strong>
                        {$isAuthenticated ? "Yes" : "No"}
                    </p>
                    <p>
                        <strong>User:</strong>
                        {$user
                            ? JSON.stringify($user, null, 2)
                            : "Not logged in"}
                    </p>
                </div>
            </div>

            <div class="mb-6">
                <h2 class="text-xl font-semibold mb-2">Test Auth Endpoint</h2>
                <button
                    onclick={testAuthEndpoint}
                    disabled={testLoading}
                    class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded disabled:opacity-50"
                >
                    {testLoading ? "Testing..." : "Test /api/auth/me Endpoint"}
                </button>

                {#if testResponse}
                    <div class="mt-4 bg-green-100 p-4 rounded">
                        <h3 class="font-semibold text-green-800">Response:</h3>
                        <pre class="mt-2 text-sm">{JSON.stringify(
                                testResponse,
                                null,
                                2,
                            )}</pre>
                    </div>
                {/if}

                {#if testError}
                    <div class="mt-4 bg-red-100 p-4 rounded">
                        <h3 class="font-semibold text-red-800">Error:</h3>
                        <p class="mt-2 text-sm">{testError}</p>
                    </div>
                {/if}
            </div>

            <div class="mt-8">
                <a href="/login" class="text-blue-500 hover:underline"
                    >Go to Login Page</a
                >
            </div>
        </div>
    </div>
</div>
