<script lang="ts">
    // Define routes for navigation items
    const navItems = [
        {
            name: "Prop Firms",
            path: "/prop_firms/",
            endpoint: "prop_firms.view_prop_firms",
        },
        {
            name: "Trades",
            path: "/trades/view",
            endpoint: "trades.view_trades",
        },
        {
            name: "Trade Pairs",
            path: "/trade_pairs",
            endpoint: "trade_pairs.index",
        },
        {
            name: "Opened trades",
            path: "/trades/list",
            endpoint: "trades.list_trades",
        },
        {
            name: "Trading Strategies",
            path: "/trading_strategies",
            endpoint: "trading_strategies.index",
        },
        {
            name: "My Strategies",
            path: "/trading_strategies/my",
            endpoint: "trading_strategies.my",
        },
        {
            name: "Profiles",
            path: "/profiles",
            endpoint: "profiles.index",
        },
    ];

    let toggleMenu = $state(false);
    let active_class = $derived(toggleMenu ? "hidden" : "");
</script>

<ul class="flex {active_class}">
    {#each navItems as item}
        <li class="mr-6">
            <a class="text-blue-500 hover:text-blue-800" href={item.path}>
                {item.name}
            </a>
        </li>
    {/each}
</ul>

<style>
    .hidden {
        display: none;
    }

    @media (max-width: 768px) {
        .environment-toggle {
            margin-top: 1rem;
        }
    }
</style>
