import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { PUBLIC_BACKEND_URL } from '$env/static/public';

export const POST: RequestHandler = async ({ request }) => {
    try {
        const formData = await request.json();

        const response = await fetch(`${PUBLIC_BACKEND_URL}/prop_firms`, {
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
        const response = await fetch(`${PUBLIC_BACKEND_URL}/prop_firms`);
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
