import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { getBackendUrl } from '$lib/stores/environment';

// Create a new prop firm
export const POST: RequestHandler = async ({ request }) => {
    try {
        const formData = await request.json();
        const backendUrl = getBackendUrl();

        const response = await fetch(`${backendUrl}/prop_firms`, {
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
            error: error instanceof Error ? error.message : 'Failed to create prop firm'
        }, { status: 500 });
    }
};

// Get all prop firms
export const GET: RequestHandler = async () => {
    try {
        const backendUrl = getBackendUrl();
        const response = await fetch(`${backendUrl}/prop_firms`);

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        return json(data);
    } catch (error) {
        console.error('Error:', error);
        return json({
            error: error instanceof Error ? error.message : 'Failed to fetch prop firms'
        }, { status: 500 });
    }
};

// Update a prop firm
export const PUT: RequestHandler = async ({ params, request }) => {
    try {
        const formData = await request.json();
        const backendUrl = getBackendUrl();

        const response = await fetch(`${backendUrl}/prop_firms/${params.id}`, {
            method: 'PUT',
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
            error: error instanceof Error ? error.message : 'Failed to update prop firm'
        }, { status: 500 });
    }
};

// Delete a prop firm
export const DELETE: RequestHandler = async ({ params }) => {
    try {
        const backendUrl = getBackendUrl();
        const response = await fetch(`${backendUrl}/prop_firms/${params.id}`, {
            method: 'DELETE'
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        return json(data);
    } catch (error) {
        console.error('Error:', error);
        return json({
            error: error instanceof Error ? error.message : 'Failed to delete prop firm'
        }, { status: 500 });
    }
};
