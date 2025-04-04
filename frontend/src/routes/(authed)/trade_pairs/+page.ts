import type { PageLoad } from './$types';
import type { TradePair } from '$lib/types/TradePairs';

export const load: PageLoad = async ({ fetch }) => {
    try {
        // Fetch data from the SvelteKit API route during server-side rendering or client-side navigation
        const response = await fetch('/api/trade_pairs');
        if (!response.ok) {
            console.error(`Failed to load trade pairs: ${response.statusText}`);
            // Return empty array or throw error depending on desired behavior
            return { pairs: [], error: `Failed to load trade pairs: ${response.statusText}` };
        }
        const pairs: TradePair[] = await response.json();
        return { pairs };
    } catch (error: any) {
        console.error('Error in load function:', error);
        // Return empty array or throw error
        return { pairs: [], error: error.message || 'Failed to load trade pairs.' };
    }
}; 