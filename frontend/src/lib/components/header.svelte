<script lang="ts">
    import { page } from "$app/state";
    let toggleMenu = $state(false);
    let active_class = $derived(toggleMenu ? "hidden" : "");

    // Define routes for navigation items
    const navItems = [
        {
            name: "Prop Firms",
            path: "/prop_firms/list",
            endpoint: "prop_firms.view_prop_firms",
        },
        {
            name: "Trades",
            path: "/trades/list",
            endpoint: "trades.view_trades",
        },
        {
            name: "Trade Pairs",
            path: "/trade_pairs/list",
            endpoint: "trade_pairs.index",
        },
        {
            name: "Trades List",
            path: "/trades/list",
            endpoint: "trades.list_trades",
        },
    ];

    function isActive(path: string) {
        return page.url.pathname === path || page.route.id?.includes(path);
    }
</script>

<nav>
    <a href="/">Trading System</a>
    <button
        onclick={() => (toggleMenu = !toggleMenu)}
        aria-label="Menu"
        class="text-blue-500 hover:text-blue-800"
    >
        <svg
            xmlns="http://www.w3.org/2000/svg"
            width="24"
            height="24"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
            class="feather feather-menu"
        >
            <line x1="3" y1="12" x2="21" y2="12"></line>
            <line x1="3" y1="6" x2="21" y2="6"></line>
            <line x1="3" y1="18" x2="21" y2="18"></line>
        </svg>
    </button>
    <ul class="flex {active_class}">
        {#each navItems as item}
            <li class="mr-6">
                <a class="text-blue-500 hover:text-blue-800" href={item.path}>
                    {item.name}
                </a>
            </li>
        {/each}
    </ul>
</nav>

<style>
    .hidden {
        display: none;
    }
</style>
