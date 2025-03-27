import type { Handle } from '@sveltejs/kit';

const ALLOWED_ORIGINS = [
    'http://localhost:5173',
    'http://localhost:3100',
    'http://100.66.179.48:3100',
    // Add other allowed domains
];

// Function to get the current backend URL based on environment
async function getBackendUrl(fetch = globalThis.fetch): Promise<string> {
    try {
        // Use the passed fetch function instead of global fetch
        const response = await fetch('http://localhost:5173/api/environment/set', {
            method: 'GET',
            headers: {
                'Accept': 'application/json'
            }
        });

        const data = await response.json();
        const environment = data.environment || 'local';

        // Return the appropriate backend URL based on environment
        if (environment === 'production') {
            return 'http://100.66.179.48:3100';
        } else {
            return 'http://localhost:3100';
        };
    } catch (error) {
        console.error('Failed to get environment, using default:', error);
        return 'http://localhost:3100'; // Default fallback
    }
}

export const handle: Handle = async ({ event, resolve }) => {
    const origin = event.request.headers.get('origin');

    // Handle preflight requests
    if (event.request.method === 'OPTIONS') {
        console.log('preflight request');
        return new Response(null, {
            headers: {
                'Access-Control-Allow-Origin': ALLOWED_ORIGINS.includes(origin ?? '')
                    ? origin!
                    : ALLOWED_ORIGINS[0],
                'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type, Authorization',
                'Access-Control-Allow-Credentials': 'true',
                'Access-Control-Max-Age': '3600'
            }
        });
    }

    // If URL starts with API, let it pass to SvelteKit
    if (event.url.pathname.startsWith('/api/')) {
        return resolve(event);
    }

    // If URL starts with python, forward it to backend
    if (event.url.pathname.startsWith('/python/')) {

        try {
            const backendUrl = await getBackendUrl(event.fetch);
            const pathWithoutPython = event.url.pathname.replace(/^\/python/, '/api');
            const targetUrl = `${backendUrl}${pathWithoutPython}${event.url.search}`;

            console.log(`Proxying request to: ${targetUrl}`);

            // Get session_id (using the correct cookie name 'session') and user_id from cookies
            const sessionId = event.cookies.get('session');
            const userId = event.cookies.get('user_id');

            // Clone existing headers and add authentication headers if cookies exist
            const requestHeaders = new Headers(event.request.headers);
            if (sessionId && userId) {
                requestHeaders.set('X-Session-ID', sessionId);
                requestHeaders.set('X-User-ID', userId);
                console.log('Added auth headers from cookies'); // Optional: for debugging
            } else {
                // Log which cookie might be missing for easier debugging
                console.log(`Auth cookies not found (session: ${!!sessionId}, user_id: ${!!userId}), forwarding without auth headers`);
            }

            // Use event.fetch instead of global fetch
            const response = await event.fetch(targetUrl, {
                method: event.request.method,
                // Use the modified headers
                headers: requestHeaders, // <-- Use the new headers object
                body: event.request.method !== 'GET' && event.request.method !== 'HEAD'
                    ? await event.request.clone().arrayBuffer()
                    : undefined,
                credentials: 'include' // Keep this if you rely on other cookies being forwarded
            });

            // Copy all headers from the backend response
            const responseHeaders = new Headers(); // Renamed to avoid conflict
            response.headers.forEach((value, key) => {
                // Avoid duplicating CORS headers if already set by backend
                if (!key.toLowerCase().startsWith('access-control-')) {
                    responseHeaders.append(key, value);
                }
            });

            // Add CORS headers if needed (ensure origin check is robust)
            if (origin && ALLOWED_ORIGINS.includes(origin)) {
                responseHeaders.set('Access-Control-Allow-Origin', origin); // Use set instead of append for single origin
                responseHeaders.set('Access-Control-Allow-Credentials', 'true');
            }

            // Create a new response with the headers and body from the backend
            return new Response(response.body, {
                status: response.status,
                statusText: response.statusText,
                headers: responseHeaders // <-- Use the new response headers object
            });
        } catch (error) {
            console.error('Error proxying request:', error);
            // Return a generic error response
            return new Response('Error proxying request', { status: 500 });
        }
    }

    const response = await resolve(event);

    // Add CORS headers to all responses
    if (origin && ALLOWED_ORIGINS.includes(origin)) {
        response.headers.append('Access-Control-Allow-Origin', origin);
        response.headers.append('Access-Control-Allow-Credentials', 'true');
    }

    return response;
};
