<script lang="ts">
    import { page } from "$app/state";
    import * as auth from "$lib/stores/auth";
    import "../app.css";
    import ToggleEnvironment from "$lib/components/ToggleEnvironment.svelte";

    // Make user data available to all child components
    let { children } = $props();

    // If we have user data from server, sync it with our client-side state
    $effect(() => {
        if (
            page.data.user &&
            JSON.stringify(page.data.user) !== JSON.stringify(auth.$user)
        ) {
            // Update client state with server data
            auth.setUser(page.data.user);
        }
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
        {:else if auth.$isAuthenticated}
            <div class="flex items-center space-x-2">
                <span>Welcome, {auth.$user?.email}</span>
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
