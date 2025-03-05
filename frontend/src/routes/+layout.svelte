<script lang="ts">
    import Header from "$lib/components/header.svelte";
    let { children } = $props();
    import "../app.css";
</script>

<Header />
{@render children()}
