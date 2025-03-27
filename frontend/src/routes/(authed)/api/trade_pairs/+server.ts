import type { RequestHandler } from '@sveltejs/kit';
import { json } from '@sveltejs/kit';

// IMPORTANT: Replace with the actual URL of your Python backend
const PYTHON_BACKEND_URL = '/python/trade_pairs/pairs'; // Or use environment variables

// GET /api/trade_pairs - Fetch all pairs
export const GET: RequestHandler = async ({ fetch }) => {
    try {
        const response = await fetch(PYTHON_BACKEND_URL);
        if (!response.ok) {
            throw new Error(`Backend error: ${response.statusText}`);
        }
        const pairs = await response.json();
        return json(pairs);
    } catch (error) {
        console.error('Error fetching trade pairs:', error);
        return json({ message: 'Failed to fetch trade pairs' }, { status: 500 });
    }
};

// POST /api/trade_pairs - Add a new pair
export const POST: RequestHandler = async ({ request, fetch }) => {
    try {
        const { name } = await request.json();
        if (!name) {
            return json({ message: 'Name is required' }, { status: 400 });
        }

        const response = await fetch(PYTHON_BACKEND_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name }),
        });

        if (!response.ok) {
            throw new Error(`Backend error: ${response.statusText}`);
        }
        const newPair = await response.json();
        return json(newPair, { status: 201 });

    } catch (error) {
        console.error('Error adding trade pair:', error);
        return json({ message: 'Failed to add trade pair' }, { status: 500 });
    }
};

// PUT /api/trade_pairs - Update an existing pair
export const PUT: RequestHandler = async ({ request, fetch }) => {
    try {
        const { id, name } = await request.json();
        if (!id || !name) {
            return json({ message: 'ID and Name are required' }, { status: 400 });
        }

        const response = await fetch(PYTHON_BACKEND_URL, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ id, name }),
        });

        if (!response.ok) {
            if (response.status === 404) {
                return json({ message: 'Trade pair not found' }, { status: 404 });
            }
            throw new Error(`Backend error: ${response.statusText}`);
        }
        const updatedPair = await response.json();
        return json(updatedPair);

    } catch (error) {
        console.error('Error updating trade pair:', error);
        return json({ message: 'Failed to update trade pair' }, { status: 500 });
    }
};

// DELETE /api/trade_pairs - Delete a pair
export const DELETE: RequestHandler = async ({ request, fetch }) => {
    try {
        const { id } = await request.json();
        if (!id) {
            return json({ message: 'ID is required' }, { status: 400 });
        }

        const response = await fetch(PYTHON_BACKEND_URL, {
            method: 'DELETE',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ id }),
        });

        if (!response.ok) {
            if (response.status === 404) {
                return json({ message: 'Trade pair not found' }, { status: 404 });
            }
            throw new Error(`Backend error: ${response.statusText}`);
        }
        // No content expected on successful delete (204)
        return new Response(null, { status: 204 });

    } catch (error) {
        console.error('Error deleting trade pair:', error);
        return json({ message: 'Failed to delete trade pair' }, { status: 500 });
    }
};
