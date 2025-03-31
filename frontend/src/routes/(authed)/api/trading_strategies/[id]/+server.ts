import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';

// Update a specific trading strategy
export const PUT: RequestHandler = async ({ request, fetch, params }: { request: any, fetch: any, params: any }) => {
    const strategyId = params.id;

    try {
        const body = await request.json();

        // Basic validation
        if (!body.name || typeof body.name !== 'string' || body.name.trim() === '') {
            return json({ error: 'Strategy name is required and must be a non-empty string' }, { status: 400 });
        }
        if (body.description && typeof body.description !== 'string') {
            return json({ error: 'Strategy description must be a string if provided' }, { status: 400 });
        }

        const response = await fetch(`/python/trading_strategies/${strategyId}`, {
            method: 'PUT',
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
            console.error(`Error updating trading strategy ${strategyId}:`, errorData);
            return json({ error: errorData.error || 'Failed to update trading strategy' }, { status: response.status });
        }

        const data = await response.json();
        return json(data);
    } catch (error) {
        console.error(`Error in PUT /api/trading_strategies/${strategyId}:`, error);
        if (error instanceof SyntaxError) {
            return json({ error: 'Invalid JSON in request body' }, { status: 400 });
        }
        const message = error instanceof Error ? error.message : 'Internal server error';
        return json({ error: message }, { status: 500 });
    }
};

// Delete a specific trading strategy
export const DELETE: RequestHandler = async ({ fetch, params }: { fetch: any, params: any }) => {
    const strategyId = params.id;

    try {
        const response = await fetch(`/python/trading_strategies/${strategyId}`, {
            method: 'DELETE',
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({ error: `HTTP error! status: ${response.status}` }));
            console.error(`Error deleting trading strategy ${strategyId}:`, errorData);
            // Attempt to parse error from backend, otherwise use status text
            return json({ error: errorData.error || 'Failed to delete trading strategy' }, { status: response.status });
        }

        // No content is expected on successful delete, often backend returns 204
        // If backend returns JSON on delete, parse it: const data = await response.json(); return json(data);
        return new Response(null, { status: 204 }); // Return 204 No Content
    } catch (error) {
        console.error(`Error in DELETE /api/trading_strategies/${strategyId}:`, error);
        const message = error instanceof Error ? error.message : 'Internal server error';
        return json({ error: message }, { status: 500 });
    }
};
