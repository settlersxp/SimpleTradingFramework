<script lang="ts">
    import * as auth from "$lib/stores/auth";

    let { showEmail = true, showId = false } = $props();
</script>

{#if auth.$isAuthenticated}
    <div class="user-profile bg-white p-4 rounded-lg shadow">
        <h2 class="text-xl font-semibold mb-2">User Profile</h2>

        {#if showEmail && auth.$user?.email}
            <div class="mb-1">
                <span class="font-medium">Email:</span>
                {auth.$user.email}
            </div>
        {/if}

        {#if showId && auth.$user?.id}
            <div class="mb-1">
                <span class="font-medium">ID:</span>
                {auth.$user.id}
            </div>
        {/if}

        {#if auth.$user?.created_at}
            <div class="mb-1">
                <span class="font-medium">Joined:</span>
                {new Date(auth.$user.created_at).toLocaleDateString()}
            </div>
        {/if}
    </div>
{:else}
    <div class="bg-gray-100 p-4 rounded-lg text-gray-500">
        User not logged in
    </div>
{/if}

<style>
    .user-profile {
        transition: all 0.2s ease;
    }

    .user-profile:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1);
    }
</style>
