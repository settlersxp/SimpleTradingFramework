<script lang="ts">
    import type { PropFirm } from "$lib/types/PropFirms";

    const props = $props<{ firm: PropFirm }>();
</script>

<div class="px-6 py-4 border-b border-gray-200">
    <h3 class="text-lg font-medium text-gray-900 mb-4">Account Information</h3>
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div>
            <p class="text-sm text-gray-500">Full Balance</p>
            <p class="text-lg font-medium text-gray-900">
                ${props.firm.full_balance
                    ? props.firm.full_balance.toFixed(2)
                    : "0.00"}
            </p>
        </div>
        <div>
            <p class="text-sm text-gray-500">Available Balance</p>
            <p class="text-lg font-medium text-gray-900">
                ${props.firm.available_balance
                    ? props.firm.available_balance.toFixed(2)
                    : "0.00"}
            </p>
        </div>
        <div>
            <p class="text-sm text-gray-500">Drawdown Percentage</p>
            <p class="text-lg font-medium text-gray-900">
                {props.firm.dowdown_percentage !== undefined
                    ? props.firm.dowdown_percentage.toFixed(2)
                    : "0.00"}%
            </p>
        </div>
    </div>
    <div class="mt-4 grid grid-cols-1 md:grid-cols-3 gap-4">
        <div>
            <p class="text-sm text-gray-500">Platform</p>
            <p class="text-lg font-medium text-gray-900">
                {props.firm.platform_type || "N/A"}
            </p>
        </div>
        <div>
            <p class="text-sm text-gray-500">Server</p>
            <p class="text-lg font-medium text-gray-900">
                {props.firm.ip_address
                    ? `${props.firm.ip_address}:${props.firm.port || "N/A"}`
                    : "N/A"}
            </p>
        </div>
    </div>
</div>
