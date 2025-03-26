import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';

// Get trades for a specific prop firm
export const GET: RequestHandler = async ({ params, fetch }: { params: any, fetch: any }) => {
    try {
        const response = await fetch(`/python/prop_firms/${params.id}/trades`);

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        return json(data);
    } catch (error) {
        console.error('Error:', error);
        return new Response(JSON.stringify({
            error: error instanceof Error ? error.message : 'Failed to fetch prop firm trades'
        }), {
            status: 500,
            headers: {
                'Content-Type': 'application/json'
            }
        });
    }
}; 