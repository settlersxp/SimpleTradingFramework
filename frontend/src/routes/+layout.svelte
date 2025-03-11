<script lang="ts">
    import Header from "$lib/components/Header.svelte";
    let { children } = $props();
    import "../app.css";
    import { onMount } from "svelte";
    import { initAuth, isAuthenticated, user } from "$lib/stores/auth";
    import { logout } from "$lib/api/auth";
    import { goto } from "$app/navigation";
    import Logo from "$lib/components/Logo.svelte";
    import ToggleEnvironment from "$lib/components/ToggleEnvironment.svelte";
    onMount(() => {
        initAuth();
    });

    // Add a reactive statement to handle redirection when not authenticated
    $effect(() => {
        if (!$isAuthenticated) {
            handleLogin();
        }
    });

    function handleLogin() {
        goto("/login");
    }
</script>

<div class="min-h-screen bg-gray-50">
    <nav
        class="flex justify-between items-center"
        style="max-width: 1200px; margin: 0 auto;"
    >
        <Logo />
        {#if $isAuthenticated}
            <div class="ml-3 relative">
                <div class="flex items-center">
                    <span class="text-sm text-gray-700 mr-4"
                        >{$user?.email}</span
                    >
                    <div class="flex items-center">
                        <Header />


                    </div>
                </div>
            </div>
        {/if}
        <ToggleEnvironment />
    </nav>

    <main>
        <div class="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
            {@render children()}
        </div>
    </main>
</div>
