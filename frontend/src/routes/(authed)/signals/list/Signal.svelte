<script lang="ts">
    import type { Signal } from "$lib/types/Signals";
    let { signal, onDelete } = $props<{
        signal: Signal;
        onDelete?: (id: number) => void;
    }>();


    async function openTrade(signalString: string) {
        const response = await fetch(`/api/trades`, {
            method: "POST",
            body: signalString,
            headers: {
                "Content-Type": "text/plain",
            },
        });

        if (!response.ok) {
            throw new Error("Failed to open trade", {
                cause: response.body,
            });
        }

        return response.json();
    }

    async function replaySignal(signalString: string) {
        const response = await fetch(`/api/signals/create`, {
            method: "POST",
            body: signalString,
        });

        if (!response.ok) {
            throw new Error("Failed to replay signal", {
                cause: response.body,
            });
        }

        return response.json();
    }

    async function deleteSignal(signalId: number) {
        const response = await fetch(`/python/signals/${signalId}`, {
            method: "DELETE",
        });

        if (!response.ok) {
            throw new Error("Failed to delete signal", {
                cause: response.body,
            });
        }

        const result = await response.json();
        onDelete?.(signalId);
        return result;
    }
</script>

<tr class="hover:bg-gray-50 transition-colors">
    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
        <button
            class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-1 px-2 rounded text-xs"
            onclick={() =>
                replaySignal(
                    `"strategy":"${signal.strategy}", "order":"${signal.order_type}", "contracts":"${signal.contracts}", "ticker":"${signal.ticker}", "position_size":"${signal.position_size}"`,
                )}
            aria-label="Replay Signal"
        >
            R
        </button>

        <button
            class="bg-red-500 hover:bg-red-700 text-white font-bold py-1 px-2 rounded text-xs"
            onclick={() => deleteSignal(signal.id)}
            aria-label="Delete Signal"
        >
            X
        </button>

        <button
            class="bg-green-500 hover:bg-green-700 text-white font-bold py-1 px-2 rounded text-xs"
            onclick={() => openTrade(
                `"strategy":"${signal.strategy}", "order":"${signal.order_type}", "contracts":"${signal.contracts}", "ticker":"${signal.ticker}", "position_size":"${signal.position_size}"`
            )}
            aria-label="Open Trade"
        >
        <svg
        xmlns="http://www.w3.org/2000/svg"
        class="h-4 w-4"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
        >
            <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z"
            />
            <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
            />
        </svg>
        </button>
    </td>
    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900"
        >{signal.id}</td
    >
    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900"
        >{signal.strategy}</td
    >
    <td class="px-6 py-4 whitespace-nowrap">
        <span
            class="px-2 py-1 text-xs font-semibold rounded-full {signal.order_type ===
            'buy'
                ? 'bg-green-100 text-green-800'
                : 'bg-red-100 text-red-800'}"
        >
            {signal.order_type.toUpperCase()}
        </span>
    </td>
    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900"
        >{signal.contracts.toFixed(3)}</td
    >
    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900"
        >{signal.ticker}</td
    >
    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900"
        >${signal.position_size.toFixed(2)}</td
    >
    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900"
        >{new Date(signal.created_at).toLocaleString()}</td
    >
</tr>
