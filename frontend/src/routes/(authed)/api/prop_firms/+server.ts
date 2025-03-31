import { json } from '@sveltejs/kit';
import type { RequestHandler } from '../$types';

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