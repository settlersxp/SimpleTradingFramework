<script lang="ts">
    type TradePairData = {
        id: number;
        name: string;
        is_associated: boolean;
        current_label: string;
    };

    type LoadData = {
        prop_firm: {
            id: number;
            name: string;
        };
        trade_pairs: TradePairData[];
    };

    const props = $props<{ data: LoadData }>();
    let tradePairs = $state<TradePairData[]>(props.data.trade_pairs);
    const propFirmName = props.data.prop_firm.name;
    const propFirmId = props.data.prop_firm.id;

    const hasChanges = $derived(() => {
        const initialPairs = JSON.stringify(props.data.trade_pairs);
        const currentPairs = JSON.stringify(tradePairs);
        return initialPairs !== currentPairs;
    });

    async function saveChanges() {
        const associations = tradePairs
            .filter((pair) => pair.is_associated)
            .map((pair) => ({
                trade_pair_id: pair.id,
                label: pair.current_label || pair.name,
            }));

        try {
            const response = await fetch(
                `/api/prop_firms/${propFirmId}/trade_pairs`,
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify({ associations }),
                },
            );

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(
                    errorData.error || `HTTP error! status: ${response.status}`,
                );
            }

            const result = await response.json();
            props.data.trade_pairs = JSON.parse(JSON.stringify(tradePairs));
        } catch (error) {
            console.error("Failed to save trade pair changes:", error);
        }
    }

    function handleCheckboxChange(pairId: number, checked: boolean) {
        tradePairs = tradePairs.map((pair) =>
            pair.id === pairId
                ? {
                      ...pair,
                      is_associated: checked,
                      current_label: checked
                          ? pair.current_label || pair.name
                          : "",
                  }
                : pair,
        );
    }

    function handleLabelChange(pairId: number, newLabel: string) {
        tradePairs = tradePairs.map((pair) =>
            pair.id === pairId ? { ...pair, current_label: newLabel } : pair,
        );
    }
</script>

<svelte:head>
    <title>Manage Trade Pairs for {propFirmName}</title>
</svelte:head>

<div class="container mx-auto p-4">
    <div class="bg-white shadow rounded-lg p-6">
        <div class="mb-6">
            <h2 class="text-2xl font-bold mb-2">
                Manage Trade Pairs for {propFirmName}
            </h2>
            <p class="text-gray-600">
                Select the trade pairs this prop firm can use and assign labels.
            </p>
            <button
                onclick={() => (window.location.href = "/prop_firms/overview")}
                class="bg-blue-500 text-white px-4 py-2 rounded"
            >
                Back to Prop Firms
            </button>
        </div>

        <div class="space-y-4">
            {#each tradePairs as pair (pair.id)}
                <div class="flex items-center space-x-4 p-2 border rounded">
                    <input
                        type="checkbox"
                        id={`pair-${pair.id}`}
                        checked={pair.is_associated}
                        onchange={(e: Event) =>
                            handleCheckboxChange(
                                pair.id,
                                (e.target as HTMLInputElement).checked,
                            )}
                        class="h-4 w-4"
                    />
                    <label for={`pair-${pair.id}`} class="flex-1 font-medium"
                        >{pair.name}</label
                    >
                    {#if pair.is_associated}
                        <input
                            type="text"
                            placeholder="Enter label (e.g., EURUSD.pro)"
                            value={pair.current_label}
                            oninput={(e: Event) =>
                                handleLabelChange(
                                    pair.id,
                                    (e.target as HTMLInputElement).value,
                                )}
                            class="border rounded px-3 py-1 w-64"
                        />
                    {/if}
                </div>
            {/each}
        </div>

        <div class="mt-6">
            <button
                onclick={saveChanges}
                disabled={!hasChanges}
                class="bg-blue-500 text-white px-4 py-2 rounded disabled:opacity-50"
            >
                Save Changes
            </button>
        </div>
    </div>
</div>
