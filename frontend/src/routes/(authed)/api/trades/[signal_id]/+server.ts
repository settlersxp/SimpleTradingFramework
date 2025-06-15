import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';

// Get a specific trade
export const GET: RequestHandler = async ({ params, fetch }: { params: any, fetch: any }) => {
    try {
        const response = await fetch(`/python/trades/${params.id}`);

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        return json(data);
    } catch (error) {
        console.error('Error fetching trade:', error);
        return json({ error: 'Failed to fetch trade' }, { status: 500 });
    }
};
