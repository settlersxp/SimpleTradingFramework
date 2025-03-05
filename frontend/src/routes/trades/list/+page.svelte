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
        fetch("http://100.66.179.48:3100/trades/")
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
