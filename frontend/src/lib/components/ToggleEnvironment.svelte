<script lang="ts">
    import { selectedEnvironment } from "$lib/stores/environment";

    function toggleEnvironment() {
        $selectedEnvironment =
            $selectedEnvironment === "local" ? "production" : "local";
    }
</script>

<div class="flex items-center">
    <div class="environment-toggle">
        <span class="mr-2 text-sm">Environment:</span>
        <button
            onclick={toggleEnvironment}
            class="px-3 py-1 rounded text-sm {$selectedEnvironment ===
            'production'
                ? 'bg-red-500 text-white'
                : 'bg-green-500 text-white'}"
        >
            {$selectedEnvironment}
        </button>
    </div>
</div>
