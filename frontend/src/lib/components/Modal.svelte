<script lang="ts">
    const props = $props<{
        show: boolean;
        title: string;
        content: string;
        onClose: () => void;
    }>();

    function handleBackdropClick(event: MouseEvent) {
        // Only close if clicking directly on the backdrop
        if (event.target === event.currentTarget) {
            props.onClose();
        }
    }

    function handleKeydown(event: KeyboardEvent) {
        if (event.key === "Escape") {
            props.onClose();
        }
    }
</script>

{#if props.show}
    <div
        class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
        onclick={handleBackdropClick}
        onkeydown={handleKeydown}
        aria-modal="true"
        role="dialog"
        tabindex="-1"
    >
        <div
            class="bg-white rounded-lg p-6 max-w-2xl w-full mx-4 max-h-[80vh] overflow-y-auto"
        >
            <div class="flex justify-between items-center mb-4">
                <h3 class="text-lg font-semibold">{props.title}</h3>
                <button
                    onclick={props.onClose}
                    class="text-gray-500 hover:text-gray-700"
                >
                    ✕
                </button>
            </div>
            <div class="prose prose-sm">
                {@html props.content}
            </div>
        </div>
    </div>
{/if}
