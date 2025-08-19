<script lang="ts">
    import { onMount, onDestroy } from "svelte";
    import {
        startAutoSync,
        stopAutoSync,
        isAutoSyncRunning,
        manualSync,
    } from "$lib/services/syncService";

    let isRunning = $state(false);
    let lastSyncResult = $state<string>("");
    let isManualSyncing = $state(false);

    onMount(() => {
        isRunning = isAutoSyncRunning();
    });

    onDestroy(() => {
        // Clean up when component is destroyed
        if (isRunning) {
            stopAutoSync();
        }
    });

    function toggleAutoSync() {
        if (isRunning) {
            stopAutoSync();
            isRunning = false;
            lastSyncResult = "Auto sync stopped";
        } else {
            startAutoSync();
            isRunning = true;
            lastSyncResult = "Auto sync started";
        }
    }

    async function handleManualSync() {
        isManualSyncing = true;
        try {
            const result = await manualSync();
            lastSyncResult = result.success
                ? `Manual sync successful: ${result.message}`
                : `Manual sync failed: ${result.error}`;
        } catch (error) {
            lastSyncResult = `Manual sync error: ${error instanceof Error ? error.message : "Unknown error"}`;
        } finally {
            isManualSyncing = false;
        }
    }
</script>

<div class="bg-white rounded-lg shadow-md p-6 mb-6">
    <h3 class="text-lg font-semibold text-gray-900 mb-4">
        Auto Sync Management
    </h3>

    <div class="flex items-center space-x-4 mb-4">
        <div class="flex items-center">
            <div
                class={`w-3 h-3 rounded-full mr-2 ${isRunning ? "bg-green-500" : "bg-red-500"}`}
            ></div>
            <span class="text-sm font-medium">
                Status: {isRunning ? "Running" : "Stopped"}
            </span>
        </div>

        {#if isRunning}
            <span class="text-xs text-gray-500">Syncing every 5 seconds</span>
        {/if}
    </div>

    <div class="flex space-x-3">
        <button
            onclick={toggleAutoSync}
            class={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                isRunning
                    ? "bg-red-600 hover:bg-red-700 text-white"
                    : "bg-green-600 hover:bg-green-700 text-white"
            }`}
        >
            {isRunning ? "Stop Auto Sync" : "Start Auto Sync"}
        </button>

        <button
            onclick={handleManualSync}
            disabled={isManualSyncing}
            class="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white rounded-md text-sm font-medium transition-colors"
        >
            {isManualSyncing ? "Syncing..." : "Manual Sync"}
        </button>
    </div>

    {#if lastSyncResult}
        <div class="mt-4 p-3 bg-gray-50 rounded-md">
            <p class="text-sm text-gray-700">{lastSyncResult}</p>
        </div>
    {/if}
</div>
