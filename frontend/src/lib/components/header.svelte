<script lang="ts">
    import { page } from "$app/state";
    import AuthHeader from "./AuthHeader.svelte";
    import Logo from "./Logo.svelte";

    $effect(() => {
        console.log("page", page);
    });
</script>

<nav>
    <div class="flex justify-between items-center w-full">
        <Logo />

        <AuthHeader />
    </div>
</nav>

<style>
    nav {
        @apply flex flex-wrap justify-between items-center;
    }
</style>
