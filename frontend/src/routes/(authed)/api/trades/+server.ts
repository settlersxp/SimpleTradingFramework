import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';

export const POST: RequestHandler = async ({ request, fetch }: { request: any, fetch: any }) => {
    try {
        const mtString = await request.text();

        const response = await fetch(`/python/trades/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'text/plain',
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
