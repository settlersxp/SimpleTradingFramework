import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';

// Get trading strategies followed by a specific user
export const GET: RequestHandler = async ({ fetch, params }: { fetch: any, params: any }) => {
    const userId = params.id;

    try {
        const response = await fetch(`/python/trading_strategies/user/${userId}`);

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({ error: `HTTP error! status: ${response.status}` }));
            console.error(`Error fetching strategies for user ${userId}:`, errorData);
            return json({ error: errorData.error || 'Failed to fetch user trading strategies' }, { status: response.status });
        }

        const data = await response.json();
        return json(data);
    } catch (error) {
        console.error(`Error in GET /python/trading_strategies/user/${userId}:`, error);
        const message = error instanceof Error ? error.message : 'Internal server error';
        return json({ error: message }, { status: 500 });
    }
};

// Update the list of trading strategies a user follows
export const POST: RequestHandler = async ({ request, fetch, params }: { request: any, fetch: any, params: any }) => {
    const userId = params.id;

    try {
        const body = await request.json();

        // Basic validation
        if (!Array.isArray(body.strategy_ids) || !body.strategy_ids.every(id => typeof id === 'number')) {
            return json({ error: 'strategy_ids must be an array of numbers' }, { status: 400 });
        }
        if (typeof body.clear_existing !== 'boolean') {
            return json({ error: 'clear_existing must be a boolean' }, { status: 400 });
        }


        const response = await fetch(`/python/trading_strategies/user/${userId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                strategy_ids: body.strategy_ids,
                clear_existing: body.clear_existing,
            }),
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({ error: `HTTP error! status: ${response.status}` }));
            console.error(`Error updating strategies for user ${userId}:`, errorData);
            return json({ error: errorData.error || 'Failed to update user trading strategies' }, { status: response.status });
        }

        // Assuming the backend might return the updated list or a success message
        const data = await response.json();
        return json(data); // Use 200 OK by default, backend might dictate otherwise
    } catch (error) {
        console.error(`Error in POST /api/trading_strategies/user/${userId}:`, error);
        if (error instanceof SyntaxError) {
            return json({ error: 'Invalid JSON in request body' }, { status: 400 });
        }
        const message = error instanceof Error ? error.message : 'Internal server error';
        return json({ error: message }, { status: 500 });
    }
};
