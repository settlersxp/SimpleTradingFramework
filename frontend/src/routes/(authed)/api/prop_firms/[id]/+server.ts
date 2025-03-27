import { json, error as svelteKitError } from '@sveltejs/kit';
import type { RequestHandler } from './$types';

// Define the base URL for your Python backend API
const PYTHON_API_BASE = '/python';

// Get a specific prop firm
export const GET: RequestHandler = async ({ params, url, fetch: skFetch }) => {
    const propFirmId = params.id;
    const resource = url.searchParams.get('resource'); // Check for 'trades' or 'trade_pairs'

    let apiUrl: string;

    if (resource === 'trades') {
        apiUrl = `${PYTHON_API_BASE}/prop_firms/${propFirmId}/trades`;
    } else if (resource === 'trade_pairs') {
        apiUrl = `${PYTHON_API_BASE}/prop_firms/${propFirmId}/trade_pairs`;
    } else if (!resource) {
        // Default: fetch the prop firm itself
        apiUrl = `${PYTHON_API_BASE}/prop_firms/${propFirmId}`;
    } else {
        throw svelteKitError(400, `Invalid resource type: ${resource}`);
    }

    try {
        console.log(`Fetching from API: ${apiUrl}`);
        const response = await skFetch(apiUrl);
        const data = await response.json();

        if (!response.ok) {
            // Use error message from Python API response if available
            throw svelteKitError(response.status, data.error || data.message || `Failed to fetch data from ${apiUrl}`);
        }

        return json(data);

    } catch (err: any) {
        console.error(`Error in GET ${url.pathname}${url.search}:`, err);
        if (err.status && err.body) throw err; // Re-throw SvelteKit errors
        throw svelteKitError(500, err.message || `Server error fetching data for prop firm ${propFirmId}.`);
    }
};

// Update a prop firm
export const PUT: RequestHandler = async ({ params, request, url, fetch: skFetch }) => {
    const propFirmId = params.id;
    const apiUrl = `${PYTHON_API_BASE}/prop_firms/${propFirmId}`;

    try {
        const requestData = await request.json(); // Expects Partial<PropFirmData>
        const response = await skFetch(apiUrl, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(requestData),
        });

        const responseData = await response.json();
        if (!response.ok) {
            throw svelteKitError(response.status, responseData.error || responseData.message || 'Failed to update prop firm');
        }
        // Python API response includes { status, message, prop_firm }
        return json(responseData);

    } catch (err: any) {
        console.error(`Error in PUT ${url.pathname}${url.search}:`, err);
        if (err.status && err.body) throw err;
        throw svelteKitError(500, err.message || `Server error updating prop firm ${propFirmId}.`);
    }
};

// Post a new trade pair association
export const POST: RequestHandler = async ({ params, request, url, fetch: skFetch }) => {
    const propFirmId = params.id;
    const resource = url.searchParams.get('resource');

    if (resource !== 'trade_pairs') {
        throw svelteKitError(400, `POST method only supported for resource=trade_pairs on this endpoint, got resource=${resource}`);
    }

    const apiUrl = `${PYTHON_API_BASE}/prop_firms/${propFirmId}/trade_pairs`;

    try {
        const requestData = await request.json(); // Expects { associations: [...] }
        const response = await skFetch(apiUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            // Ensure the body matches what the Python API expects
            body: JSON.stringify({ associations: requestData.associations }),
        });

        const responseData = await response.json();
        if (!response.ok) {
            throw svelteKitError(response.status, responseData.error || responseData.message || 'Failed to update trade pair associations');
        }
        // Python API returns { status, message }
        return json(responseData);

    } catch (err: any) {
        console.error(`Error in POST ${url.pathname}${url.search}:`, err);
        if (err.status && err.body) throw err;
        throw svelteKitError(500, err.message || `Server error updating trade pairs for prop firm ${propFirmId}.`);
    }
};

// Delete a prop firm
export const DELETE: RequestHandler = async ({ params, url, fetch: skFetch }) => {
    const propFirmId = params.id;
    const apiUrl = `${PYTHON_API_BASE}/prop_firms/${propFirmId}`;

    try {
        const response = await skFetch(apiUrl, { method: 'DELETE' });

        if (!response.ok) {
            try {
                const errorData = await response.json();
                throw svelteKitError(response.status, errorData.error || errorData.message || response.statusText);
            } catch (e) { // Handle non-JSON error response
                throw svelteKitError(response.status, response.statusText);
            }
        }

        // Handle potential 200 with JSON or 204 No Content from Python API
        const text = await response.text();
        try {
            const responseData = text ? JSON.parse(text) : {};
            return json({ success: true, message: responseData.message || 'Prop firm deleted successfully' });
        } catch (e) {
            // Handle 204 No Content or non-JSON success response
            return json({ success: true, message: 'Prop firm deleted successfully' });
        }

    } catch (err: any) {
        console.error(`Error in DELETE ${url.pathname}${url.search}:`, err);
        if (err.status && err.body) throw err;
        throw svelteKitError(500, err.message || `Server error deleting prop firm ${propFirmId}.`);
    }
}; 