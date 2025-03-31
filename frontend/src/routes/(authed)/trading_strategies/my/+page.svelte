<script lang="ts">
    import UserTradingStrategySelector from "$lib/components/UserTradingStrategySelector.svelte";
    import { page } from "$app/stores";
</script>

<div class="container mx-auto px-4 py-8">
    <h1 class="text-3xl font-bold mb-8">My Trading Strategies</h1>
    <p class="mb-6">
        Select the trading strategies you want to follow and track in your
        account.
    </p>

    <div class="bg-white rounded-lg shadow">
        <UserTradingStrategySelector userId={$page.data.user.id} />
    </div>
</div>
