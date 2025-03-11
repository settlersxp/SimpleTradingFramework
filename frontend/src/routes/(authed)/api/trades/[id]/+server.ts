import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { getBackendUrl } from '$lib/stores/environment';

// Get a specific trade
export const GET: RequestHandler = async ({ params }) => {
    try {
        const backendUrl = getBackendUrl();
        const response = await fetch(`${backendUrl}/trades/${params.id}`);

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

// Delete a trade
export const DELETE: RequestHandler = async ({ params }) => {
    try {
        const backendUrl = getBackendUrl();
        const response = await fetch(`${backendUrl}/trades/${params.id}`, {
            method: 'DELETE'
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        return json(data);
    } catch (error) {
        console.error('Error deleting trade:', error);
        return json({ error: 'Failed to delete trade' }, { status: 500 });
    }
}; 