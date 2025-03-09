import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { getBackendUrl } from '$lib/stores/environment';

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
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        return json(data);
    } catch (error) {
        console.error('Error:', error);
        return new Response(JSON.stringify({ error: 'Failed to create prop firm' }), {
            status: 500,
            headers: {
                'Content-Type': 'application/json'
            }
        });
    }
};

export const GET: RequestHandler = async () => {
    try {
        const backendUrl = getBackendUrl();
        const response = await fetch(`${backendUrl}/prop_firms`);
        const data = await response.json();
        return json(data);
    } catch (error) {
        console.error('Error:', error);
        return new Response(JSON.stringify({ error: 'Failed to fetch prop firms' }), {
            status: 500,
            headers: {
                'Content-Type': 'application/json'
            }
        });
    }
};
