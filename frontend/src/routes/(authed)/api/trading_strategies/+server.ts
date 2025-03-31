import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';

// Get all trading strategies
export const GET: RequestHandler = async ({ fetch }: { fetch: any }) => {
    try {
        const response = await fetch(`/python/trading_strategies`);

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({ error: `HTTP error! status: ${response.status}` }));
            console.error('Error fetching all trading strategies:', errorData);
            return json({ error: errorData.error || 'Failed to fetch trading strategies' }, { status: response.status });
        }

        const data = await response.json();
        return json(data);
    } catch (error) {
        console.error('Error in GET /api/trading_strategies:', error);
        const message = error instanceof Error ? error.message : 'Internal server error';
        return json({ error: message }, { status: 500 });
    }
};

// Create a new trading strategy
export const POST: RequestHandler = async ({ request, fetch }: { request: any, fetch: any }) => {
    try {
        const body = await request.json();

        // Basic validation (consider more robust validation)
        if (!body.name || typeof body.name !== 'string' || body.name.trim() === '') {
            return json({ error: 'Strategy name is required and must be a non-empty string' }, { status: 400 });
        }
        if (body.description && typeof body.description !== 'string') {
            return json({ error: 'Strategy description must be a string if provided' }, { status: 400 });
        }


        const response = await fetch(`/python/trading_strategies`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                name: body.name.trim(),
                description: body.description ? body.description.trim() : null,
            }),
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({ error: `HTTP error! status: ${response.status}` }));
            console.error('Error creating trading strategy:', errorData);
            return json({ error: errorData.error || 'Failed to create trading strategy' }, { status: response.status });
        }

        const data = await response.json();
        return json(data, { status: 201 }); // Return 201 Created status
    } catch (error) {
        console.error('Error in POST /api/trading_strategies:', error);
        if (error instanceof SyntaxError) {
            return json({ error: 'Invalid JSON in request body' }, { status: 400 });
        }
        const message = error instanceof Error ? error.message : 'Internal server error';
        return json({ error: message }, { status: 500 });
    }
};
