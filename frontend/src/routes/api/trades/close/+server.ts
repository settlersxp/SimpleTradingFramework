import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { getBackendUrl } from '$lib/stores/environment';

// Close a trade
export const GET: RequestHandler = async ({ url }) => {
    try {
        const backendUrl = getBackendUrl();
        const tradeId = url.searchParams.get('trade_id');

        if (!tradeId) {
            return json({ error: 'Missing trade_id parameter' }, { status: 400 });
        }

        const response = await fetch(`${backendUrl}/trades/close?trade_id=${tradeId}`, {
            method: 'GET'
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        return json(data);
    } catch (error) {
        console.error('Error closing trade:', error);
        return json({ error: 'Failed to close trade' }, { status: 500 });
    }
}; 