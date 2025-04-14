<script lang="ts">
    import { goto } from "$app/navigation";
    import * as auth from "$lib/stores/auth";
    import Login from "./login/+page.svelte";

    $: if (auth.$user) {
        goto("/prop_firms/overview");
    }
</script>

{#if !auth.$user}
    <Login />
{/if}
