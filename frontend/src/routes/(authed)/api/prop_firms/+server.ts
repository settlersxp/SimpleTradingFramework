import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';

// Create a new prop firm
export const POST: RequestHandler = async ({ request, fetch }: { request: any, fetch: any }) => {
    try {
        const formData = await request.json();

        const response = await fetch(`/python/prop_firms`, {
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
export const GET: RequestHandler = async ({ fetch }: { fetch: any }) => {
    try {
        const response = await fetch(`/python/prop_firms/`);

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
export const PUT: RequestHandler = async ({ params, request, fetch }: { params: any, request: any, fetch: any }) => {
    try {
        const formData = await request.json();

        const response = await fetch(`/python/prop_firms/${params.id}`, {
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
export const DELETE: RequestHandler = async ({ params, fetch }: { params: any, fetch: any }) => {
    try {
        const response = await fetch(`/python/prop_firms/${params.id}`, {
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
