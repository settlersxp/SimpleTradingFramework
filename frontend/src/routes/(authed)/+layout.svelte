<script lang="ts">
    import AuthHeader from "$lib/components/AuthHeader.svelte";

    let { data, children } = $props();

    $effect(() => {
        console.log("user_data", data);
    });
</script>

<div class="py-10">
    <header
        class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-4 border-b border-gray-200"
    >
        <div class="flex justify-between items-center">
            {#if data.user}
                <AuthHeader />
            {:else}
                <h1 class="text-3xl font-bold leading-tight text-gray-900">
                    Trading App
                </h1>
            {/if}
        </div>
    </header>

    <main>
        <div class="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
            {@render children()}
        </div>
    </main>
</div>
