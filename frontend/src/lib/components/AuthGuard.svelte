<script lang="ts">
    import { onMount } from "svelte";
    import { goto } from "$app/navigation";
    import { isAuthenticated, isLoading } from "$lib/stores/auth";

    export let redirectTo = "/login";

    onMount(() => {
        const unsubscribe = isLoading.subscribe((loading) => {
            if (!loading) {
                isAuthenticated.subscribe((authenticated) => {
                    if (!authenticated) {
                        goto(redirectTo);
                    }
                });
            }
        });

        return unsubscribe;
    });
</script>

{#if $isLoading}
    <div class="flex justify-center items-center h-screen">
        <div
            class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-indigo-500"
        ></div>
    </div>
{:else if $isAuthenticated}
    <slot />
{/if}
