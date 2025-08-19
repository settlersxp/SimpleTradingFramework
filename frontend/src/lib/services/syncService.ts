/**
 * Service for automatically syncing prop firms every 5 seconds
 */

let intervalId: NodeJS.Timeout | null = null;
let isRunning = false;

interface SyncResponse {
    success: boolean;
    message: string;
    results?: Record<string, any>;
    error?: string;
}

/**
 * Calls the public sync endpoint without authentication
 */
async function syncPropFirms(): Promise<SyncResponse> {
    try {
        const response = await fetch('/python/prop_firms/sync_public', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({}) // Empty body to sync all active firms
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return await response.json();
    } catch (error) {
        console.error('Error syncing prop firms:', error);
        return {
            success: false,
            error: error instanceof Error ? error.message : 'Unknown error occurred'
        };
    }
}

/**
 * Starts the automatic sync process (every 5 seconds)
 */
export function startAutoSync(): void {
    if (isRunning) {
        console.warn('Auto sync is already running');
        return;
    }

    console.log('Starting automatic prop firm sync (every 5 seconds)');

    // Sync immediately
    syncPropFirms().then(result => {
        console.log('Initial sync result:', result);
    });

    // Then sync every 5 seconds
    intervalId = setInterval(async () => {
        const result = await syncPropFirms();
        console.log('Auto sync result:', result);

        if (!result.success) {
            console.error('Auto sync failed:', result.error);
        }
    }, 5000);

    isRunning = true;
}

/**
 * Stops the automatic sync process
 */
export function stopAutoSync(): void {
    if (intervalId) {
        clearInterval(intervalId);
        intervalId = null;
        isRunning = false;
        console.log('Stopped automatic prop firm sync');
    }
}

/**
 * Checks if auto sync is currently running
 */
export function isAutoSyncRunning(): boolean {
    return isRunning;
}

/**
 * Manually trigger a sync (useful for testing or immediate sync needs)
 */
export async function manualSync(): Promise<SyncResponse> {
    console.log('Manual sync triggered');
    return await syncPropFirms();
}
