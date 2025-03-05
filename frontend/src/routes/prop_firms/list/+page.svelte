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
        fetch("http://100.66.179.48:3100/prop_firms/")
            .then((res) => res.json())
            .then((data) => (prop_firms = data as PropFirm[]));
    });
</script>

<div>
    <h1>Prop Firms</h1>
    <ul>
        {#each prop_firms as prop_firm}
            <li>{prop_firm.name}</li>
        {/each}
    </ul>
</div>
