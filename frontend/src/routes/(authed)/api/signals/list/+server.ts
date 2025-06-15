// Router for the signals endpoint
import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';

// Get all trades
export const GET: RequestHandler = async ({ fetch }: { fetch: any }) => {
    try {

        const response = await fetch(`/python/signals/list`);

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        return json(data);
    } catch (error) {
        console.error('Error fetching trades:', error);
        return json({ error: 'Failed to fetch trades' }, { status: 500 });
    }
};
