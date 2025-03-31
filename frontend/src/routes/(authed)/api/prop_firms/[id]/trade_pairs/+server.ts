import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';

// Get trade pairs for a prop firm
export const GET: RequestHandler = async ({ params, fetch }: { params: any, fetch: any }) => {
    try {
        const response = await fetch(`/python/prop_firms/${params.id}/trade_pairs`);

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        return json(data);
    } catch (error) {
        console.error('Error:', error);
        return json({
            error: error instanceof Error ? error.message : 'Failed to fetch trade pairs'
        }, { status: 500 });
    }
};

// Update trade pair associations
export const POST: RequestHandler = async ({ params, request, fetch }: { params: any, request: any, fetch: any }) => {
    try {
        const formData = await request.json();

        const response = await fetch(`/python/prop_firms/${params.id}/trade_pairs`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.message || `HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        return json(data);
    } catch (error) {
        console.error('Error:', error);
        return json({
            error: error instanceof Error ? error.message : 'Failed to update trade pairs'
        }, { status: 500 });
    }
}; 