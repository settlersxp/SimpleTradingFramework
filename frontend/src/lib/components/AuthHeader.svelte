<script lang="ts">
    // Define routes for navigation items
    const navItems = [
        {
            name: "Prop Firms",
            path: "/prop_firms/",
        },
        {
            name: "Trades",
            path: "/trades/view",
        },
        {
            name: "Trade Pairs",
            path: "/trade_pairs",
        },
        {
            name: "Saved signals",
            path: "/signals/list",
        },
        {
            name: "Trading Strategies",
            path: "/trading_strategies",
        },
        {
            name: "My Strategies",
            path: "/trading_strategies/my",
        },
        {
            name: "Profiles",
            path: "/profiles",
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
