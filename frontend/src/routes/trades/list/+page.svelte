<script lang="ts">
    let trades = $state<Trade[]>([]);

    type Trade = {
        id: number;
        name: string;
        description: string;
        created_at: string;
        updated_at: string;
    };
    $effect(() => {
        fetch("api/trades/",
            {
                method: "GET",
                headers: {
                    "Content-Type": "application/json",
                },
            }
        )
            .then((res) => res.json())
            .then((data) => (trades = data as Trade[]));
    });
</script>

<p>trades list</p>
<ul>
    {#each trades as trade}
        <li><a href={`/trades/${trade.id}`}>{trade.id}</a></li>
    {/each}
</ul>
