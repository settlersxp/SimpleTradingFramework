<script lang="ts">
    import type { TradeWithFirm } from "$lib/types/TradeWithFirm";
    let { trade } = $props<{ trade: TradeWithFirm }>();
</script>

<tr class="hover:bg-gray-50 transition-colors">
    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{trade.id}</td
    >
    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900"
        >{trade.strategy}</td
    >
    <td class="px-6 py-4 whitespace-nowrap">
        <span
            class="px-2 py-1 text-xs font-semibold rounded-full {trade.order_type ===
            'buy'
                ? 'bg-green-100 text-green-800'
                : 'bg-red-100 text-red-800'}"
        >
            {trade.order_type.toUpperCase()}
        </span>
    </td>
    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900"
        >{trade.contracts.toFixed(3)}</td
    >
    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900"
        >{trade.ticker}</td
    >
    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900"
        >${trade.position_size.toFixed(2)}</td
    >
    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900"
        >{new Date(trade.created_at).toLocaleString()}</td
    >
    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900"
        >{trade.prop_firm.name}</td
    >
</tr>
