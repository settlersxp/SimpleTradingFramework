<script lang="ts">
    type PropFirm = {
        id: number;
        name: string;
        description: string;
        created_at: string;
        updated_at: string;
    };

    let prop_firms = $state<PropFirm[]>([]);

    $effect(() => {
        fetch("/api/prop_firms", {
            method: "GET",
            headers: {
                "Content-Type": "application/json",
            },
        })
            .then((res) => res.json())
            .then((data) => (prop_firms = data as PropFirm[]));
    });
</script>

<div>
    <h1>Prop Firms</h1>
    <a href="/prop_firms/" class="bg-blue-500 text-white px-4 py-2 rounded-md">
        New
    </a>
    <ul>
        {#each prop_firms as prop_firm}
            <li>{prop_firm.name}</li>
        {/each}
    </ul>
</div>
