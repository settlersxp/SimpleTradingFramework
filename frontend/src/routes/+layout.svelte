<script lang="ts">
    // No need to import 'page' store anymore
    import * as auth from "$lib/stores/auth";
    import "../app.css";
    import ToggleEnvironment from "$lib/components/ToggleEnvironment.svelte";

    // Destructure 'data' and 'children' from $props
    // 'data' contains the result from your +layout.server.ts load function
    let { data, children } = $props();

    // Effect to sync server data with client store
    $effect(() => {
        console.log("Layout effect running with data.user:", data.user);
        auth.setUser(data.user);
        // Add log to see store state right after calling setUser in the effect
        console.log("Store state after setUser in effect:", {
            user: auth.$user,
            isLoading: auth.$isLoading,
            isAuthenticated: auth.$isAuthenticated,
        });
    });
</script>

<div class="min-h-screen bg-gray-50">
    <nav
        class="flex justify-between items-center"
        style="max-width: 1200px; margin: 0 auto;"
    >
        <ToggleEnvironment />

        {#if auth.$isLoading}
            <span>Loading...</span>
        {:else if auth.$user}
            <div class="flex items-center space-x-2">
                <span class="text-gray-700 mr-4"
                    >Welcome, {auth.$user?.email}</span
                >

                <a href="/logout" class="text-blue-500 hover:underline"
                    >Logout</a
                >
            </div>
        {:else}
            <div class="space-x-2">
                <a href="/login" class="text-blue-500 hover:underline">Login</a>
                <a href="/register" class="text-blue-500 hover:underline"
                    >Register</a
                >
            </div>
        {/if}
    </nav>

    <main>
        <div class="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
            {@render children()}
        </div>
    </main>
</div>
