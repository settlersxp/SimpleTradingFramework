import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';

export const POST: RequestHandler = async ({ request, fetch }) => {
    try {
        const data = await request.json();
        const response = await fetch(`/python/prop_firms/sync`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });

        if (!response.ok) {
            const error = await response.json();
            return json(error, { status: response.status });
        }

        return json(await response.json());
    } catch (error) {
        console.error('Error in sync endpoint:', error);
        return json({
            success: false,
            error: error instanceof Error ? error.message : 'An unknown error occurred'
        }, { status: 500 });
    }
}; 