<script lang="ts">
    import type { Signal } from "$lib/types/Signals";
    let { signal } = $props<{ signal: Signal }>();
</script>

<tr class="hover:bg-gray-50 transition-colors">
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
