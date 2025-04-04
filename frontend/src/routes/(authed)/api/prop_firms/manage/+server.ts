import { json, error as svelteKitError } from '@sveltejs/kit';
import type { RequestHandler } from './$types';

// Define the base URL for your Python backend API
const PYTHON_API_BASE = '/python';

// --- GET Handler ---
// Handles fetching all prop firms, a single prop firm by ID, or user-specific prop firms
export const GET: RequestHandler = async ({ url, fetch: skFetch }) => {
    const propFirmId = url.searchParams.get('id');
    const getUserFirms = url.searchParams.get('user') === 'true';
    // Add params for other resources like trades or trade_pairs if needed
    // const resource = url.searchParams.get('resource');

    let apiUrl: string;

    if (getUserFirms) {
        apiUrl = `${PYTHON_API_BASE}/user_prop_firms/user/prop_firms`;
    } else if (propFirmId) {
        // if (resource === 'trades') {
        //     apiUrl = `${PYTHON_API_BASE}/prop_firms/${propFirmId}/trades`;
        // } else if (resource === 'trade_pairs') {
        //     apiUrl = `${PYTHON_API_BASE}/prop_firms/${propFirmId}/trade_pairs`;
        // } else {
        apiUrl = `${PYTHON_API_BASE}/prop_firms/${propFirmId}`;
        // }
    } else {
        apiUrl = `${PYTHON_API_BASE}/prop_firms`;
    }

    try {
        // Use the SvelteKit fetch wrapper `skFetch` which handles credentials/cookies
        const response = await skFetch(apiUrl);
        const data = await response.json();

        if (!response.ok) {
            // Use error message from Python API response if available
            throw svelteKitError(response.status, data.error || data.message || `Failed to fetch data from ${apiUrl}`);
        }

        // The Python backend might return data directly (object/array) or wrapped { prop_firms: [...] }
        // Return the data as received. The caller (+page.ts) will handle the structure.
        return json(data);

    } catch (err: any) {
        // Log the error on the server
        console.error(`Error in GET ${url.pathname}${url.search}:`, err);
        // If it's already a SvelteKit error, rethrow it
        if (err.status && err.body) throw err;
        // Otherwise, create a generic server error response
        throw svelteKitError(500, err.message || 'An unexpected server error occurred while fetching prop firm data.');
    }
};

// --- POST Handler ---
// Handles associating a prop firm with a user OR creating a new prop firm
// We differentiate based on the request body structure.
export const POST: RequestHandler = async ({ request, url, fetch: skFetch }) => {
    const requestData = await request.json();

    // Check if it's a user association request (based on previous implementation)
    if (requestData.action && requestData.propFirmId && (requestData.action === 'add' || requestData.action === 'remove')) {
        const { action, propFirmId } = requestData;
        const apiUrl = `${PYTHON_API_BASE}/user_prop_firms/user/prop_firms/${propFirmId}`;
        const method = action === 'add' ? 'POST' : 'DELETE'; // Map add/remove to POST/DELETE

        try {
            const response = await skFetch(apiUrl, { method });

            // Handle potential non-JSON or error responses from Python API
            if (!response.ok) {
                try {
                    const errorData = await response.json();
                    throw svelteKitError(response.status, errorData.error || errorData.message || response.statusText);
                } catch (e) { // Handle non-JSON error response
                    throw svelteKitError(response.status, response.statusText);
                }
            }

            // Try parsing JSON for success message, handle 204 No Content
            const text = await response.text();
            try {
                const data = text ? JSON.parse(text) : {};
                return json({ success: true, message: data.message || `Prop firm association ${action === 'add' ? 'added' : 'removed'} successfully.` });
            } catch (e) {
                // If parsing fails but status was ok, assume success (e.g. 204)
                return json({ success: true, message: `Prop firm association ${action === 'add' ? 'added' : 'removed'} successfully.` });
            }
        } catch (err: any) {
            console.error(`Error in POST ${url.pathname} (user association):`, err);
            if (err.status && err.body) throw err;
            throw svelteKitError(500, err.message || 'Server error updating user prop firm association.');
        }
    }
    // Check if it's a request to update trade pairs (based on old API client)
    else if (requestData.associations && url.searchParams.has('id') && url.searchParams.get('resource') === 'trade_pairs') {
        const propFirmId = url.searchParams.get('id');
        const apiUrl = `${PYTHON_API_BASE}/prop_firms/${propFirmId}/trade_pairs`;
        try {
            const response = await skFetch(apiUrl, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ associations: requestData.associations }), // Python API expects {"associations": [...]}
            });
            const responseData = await response.json();
            if (!response.ok) {
                throw svelteKitError(response.status, responseData.error || responseData.message || 'Failed to update trade pair associations');
            }
            return json(responseData); // Python API returns { status, message }
        } catch (err: any) {
            console.error(`Error in POST ${url.pathname} (trade pairs):`, err);
            if (err.status && err.body) throw err;
            throw svelteKitError(500, err.message || 'Server error updating trade pair associations.');
        }
    }
    // Otherwise, assume it's a request to create a new prop firm
    else {
        const apiUrl = `${PYTHON_API_BASE}/prop_firms`;
        try {
            const response = await skFetch(apiUrl, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(requestData), // Pass the full body as PropFirmData
            });
            const responseData = await response.json();
            if (!response.ok) {
                throw svelteKitError(response.status, responseData.error || responseData.message || 'Failed to create prop firm');
            }
            // Python API response includes { status, message, prop_firm }
            return json(responseData);
        } catch (err: any) {
            console.error(`Error in POST ${url.pathname} (create prop firm):`, err);
            if (err.status && err.body) throw err;
            throw svelteKitError(500, err.message || 'Server error creating prop firm.');
        }
    }
};

// --- PUT Handler (Handles Prop Firm Update) ---
// Requires ID as a query parameter: ?id=<propFirmId>
export const PUT: RequestHandler = async ({ request, url, fetch: skFetch }) => {
    const propFirmId = url.searchParams.get('id');
    if (!propFirmId) {
        throw svelteKitError(400, 'Invalid request: Prop firm ID required as query parameter (?id=...).');
    }

    const apiUrl = `${PYTHON_API_BASE}/prop_firms/${propFirmId}`;
    try {
        const data = await request.json(); // Expects Partial<PropFirmData>
        const response = await skFetch(apiUrl, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data),
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
        throw svelteKitError(500, err.message || 'Server error updating prop firm.');
    }
};

// --- DELETE Handler (Handles Prop Firm Deletion) ---
// Requires ID as a query parameter: ?id=<propFirmId>
export const DELETE: RequestHandler = async ({ url, fetch: skFetch }) => {
    const propFirmId = url.searchParams.get('id');
    if (!propFirmId) {
        // If ID is not in query, maybe it's a user association removal?
        // This conflicts with the POST handler's logic. Sticking to query param for direct deletion.
        throw svelteKitError(400, 'Invalid request: Prop firm ID required as query parameter (?id=...) for deletion.');
    }

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
        throw svelteKitError(500, err.message || 'Server error deleting prop firm.');
    }
}; 