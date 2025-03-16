import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { getBackendUrl } from '$lib/stores/environment';

// Get trade pairs for a prop firm
export const GET: RequestHandler = async ({ params }) => {
    try {
        const backendUrl = getBackendUrl();
        const response = await fetch(`${backendUrl}/prop_firms/${params.id}/trade_pairs`);

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
export const POST: RequestHandler = async ({ params, request }) => {
    try {
        const formData = await request.json();
        const backendUrl = getBackendUrl();

        const response = await fetch(`${backendUrl}/prop_firms/${params.id}/trade_pairs`, {
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