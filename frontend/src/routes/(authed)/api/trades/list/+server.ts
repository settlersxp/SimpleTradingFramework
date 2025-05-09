// Router for the trades endpoint
import { json } from '@sveltejs/kit';
import type { RequestHandler } from '../$types';

// Get all trades
export const GET: RequestHandler = async ({ fetch }: { fetch: any }) => {
    try {

        const response = await fetch(`/python/trades/view`);

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

// Create a new trade
export const POST: RequestHandler = async ({ request, fetch }: { request: any, fetch: any }) => {
    try {
        const mtString = await request.text();

        const response = await fetch(`/python/trades`, {
            method: 'POST',
            headers: {
                'Content-Type': 'text/plain'
            },
            body: mtString
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        return json(data);
    } catch (error) {
        console.error('Error creating trade:', error);
        return json({ error: 'Failed to create trade' }, { status: 500 });
    }
};

