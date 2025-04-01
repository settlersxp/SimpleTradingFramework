import type { Handle } from '@sveltejs/kit';
// Assuming Node 18+ where fetch is global.
// If using older Node or for explicit clarity, you might install and import node-fetch:
// import fetch from 'node-fetch';

const ALLOWED_ORIGINS = [
    'http://localhost:5173',
    'http://localhost:3100',
    'http://100.66.179.48:3100',
    // Add other allowed domains
];

// Function to get the current backend URL based on environment
async function getBackendUrl(fetchFn = globalThis.fetch): Promise<string> {
    try {
        // Use the passed fetch function (which might be event.fetch or globalThis.fetch)
        const response = await fetchFn('http://localhost:5173/api/environment/set', {
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

    // If URL starts with python, forward it to backend using standard fetch
    if (event.url.pathname.startsWith('/python/')) {

        try {
            // Use event.fetch for getting backend URL as it's an internal call conceptually
            const backendUrl = await getBackendUrl(event.fetch);
            const pathWithoutPython = event.url.pathname.replace(/^\/python/, '/api');
            const targetUrl = `${backendUrl}${pathWithoutPython}${event.url.search}`;

            console.log(`Proxying request using standard fetch to: ${targetUrl}`);

            const sessionId = event.cookies.get('session');
            const userId = event.cookies.get('user_id');

            // --- Manually Construct Headers ---
            const requestHeaders = new Headers();

            // Copy *most* headers from the original request
            // Be selective: avoid headers like Host, Connection, keep-alive, etc.
            // that are connection-specific or might break the proxy.
            const headersToSkip = ['host', 'connection', 'keep-alive', 'transfer-encoding', 'content-length', 'cookie']; // Add others if needed
            event.request.headers.forEach((value, key) => {
                if (!headersToSkip.includes(key.toLowerCase())) {
                    requestHeaders.set(key, value);
                }
            });

            // Add custom auth headers
            if (sessionId && userId) {
                requestHeaders.set('X-Session-ID', sessionId);
                requestHeaders.set('X-User-ID', userId);
                console.log('Added auth X-headers');
            } else {
                console.log(`Auth cookies not found (session: ${!!sessionId}, user_id: ${!!userId}), forwarding without X-headers`);
            }

            // --- Handle Body ---
            let bodyToSend: BodyInit | null = null;
            if (event.request.method !== 'GET' && event.request.method !== 'HEAD') {
                bodyToSend = event.request.clone().body;
            }

            // --- Use standard 'fetch' ---
            const backendResponse = await fetch(targetUrl, { // Use global fetch
                method: event.request.method,
                headers: requestHeaders,
                body: bodyToSend,
                // Required for request bodies in Node fetch
                duplex: 'half'
                // `credentials: 'include'` is NOT used with standard fetch; cookies handled manually above if needed
            });

            // --- Process Backend Response ---
            const responseHeaders = new Headers();
            backendResponse.headers.forEach((value, key) => {
                // Avoid copying hop-by-hop headers or problematic ones
                const lowerKey = key.toLowerCase();
                if (lowerKey !== 'content-encoding' && lowerKey !== 'transfer-encoding' && lowerKey !== 'connection') {
                    // Also avoid duplicating CORS headers if already set by backend
                    if (!lowerKey.startsWith('access-control-')) {
                        responseHeaders.append(key, value);
                    }
                }
            });

            // Add CORS headers (ensure origin check is robust)
            if (origin && ALLOWED_ORIGINS.includes(origin)) {
                responseHeaders.set('Access-Control-Allow-Origin', origin);
                responseHeaders.set('Access-Control-Allow-Credentials', 'true');
                // Add other CORS headers from OPTIONS response if needed for the actual response
                responseHeaders.set('Access-Control-Expose-Headers', '*'); // Or be more specific
            }

            return new Response(backendResponse.body, {
                status: backendResponse.status,
                statusText: backendResponse.statusText,
                headers: responseHeaders
            });

        } catch (error) {
            console.error('Error proxying request with standard fetch:', error);
            return new Response('Error proxying request', { status: 500 });
        }
    }

    // --- Populate locals for SvelteKit routes ---
    const userIdCookie = event.cookies.get('user_id');
    if (userIdCookie) {
        try {
            const userId = parseInt(userIdCookie, 10);
            if (!isNaN(userId)) {
                event.locals.user = { id: userId };
                console.log(`Populated event.locals.user with ID: ${userId}`);
            } else {
                console.warn(`Failed to parse user_id cookie: '${userIdCookie}'`);
            }
        } catch (error) {
            console.error('Error processing user_id cookie:', error);
        }
    } else {
        console.log('user_id cookie not found, event.locals.user not set.');
    }

    const response = await resolve(event);

    // Add CORS headers to all responses
    if (origin && ALLOWED_ORIGINS.includes(origin)) {
        response.headers.append('Access-Control-Allow-Origin', origin);
        response.headers.append('Access-Control-Allow-Credentials', 'true');
    }

    return response;
};
