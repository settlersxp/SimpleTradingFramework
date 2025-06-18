<script lang="ts">
    import type { PropFirm } from "$lib/types/PropFirms";
    import Modal from "$lib/components/Modal.svelte";

    const props = $props<{
        firm: PropFirm;
        syncing: boolean;
        onSync: (firmId: number) => void;
        onToggleStatus: (firmId: number, status: boolean) => void;
    }>();

    let showDescription = $state(false);

    function renderDescription() {
        const content = props.firm.description || "No description available.";
        return `<div>${content}</div>`;
    }
</script>

<div class="px-6 py-4 bg-gray-50 border-b border-gray-200">
    <div class="flex justify-between items-center">
        <h2 class="text-xl font-semibold text-gray-800">
            {props.firm.name}
        </h2>
        <div class="flex items-center space-x-4">
            <button
                class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-1 px-2 rounded text-xs"
                onclick={() => (showDescription = true)}
            >
                Description
            </button>
            <button
                onclick={() =>
                    props.onToggleStatus(props.firm.id, !props.firm.is_active)}
                class={`px-3 py-1 rounded-full text-sm font-medium ${props.firm.is_active ? "bg-green-100 text-green-800" : "bg-red-100 text-red-800"}`}
            >
                {props.firm.is_active ? "Active" : "Inactive"}
            </button>
            <button
                onclick={() => props.onSync(props.firm.id)}
                disabled={props.syncing}
                class="bg-gray-100 text-gray-700 px-3 py-1 rounded hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed"
            >
                {props.syncing ? "Syncing..." : "Sync"}
            </button>
            <button
                class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-1 px-2 rounded text-xs"
                onclick={() =>
                    (window.location.href = `/prop_firms/${props.firm.id}`)}
            >
                Manage
            </button>
        </div>
    </div>
</div>

<Modal
    show={showDescription}
    title="Description"
    onClose={() => (showDescription = false)}
    content={renderDescription()}
/>
