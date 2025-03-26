import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';

// Replay a trade
export const POST: RequestHandler = async ({ params, fetch }: { params: any, fetch: any }) => {
    try {
        const response = await fetch(`/python/trades/${params.id}/replay`, {
            method: 'POST'
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        return json(data);
    } catch (error) {
        console.error('Error replaying trade:', error);
        return json({ error: 'Failed to replay trade' }, { status: 500 });
    }
}; 