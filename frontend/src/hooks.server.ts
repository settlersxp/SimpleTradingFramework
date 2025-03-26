import type { Handle } from '@sveltejs/kit';

const ALLOWED_ORIGINS = [
    'http://localhost:5173',
    'http://localhost:3100',
    'http://100.66.179.48:3100',
    // Add other allowed domains
];

// Function to get the current backend URL based on environment
async function getBackendUrl(): Promise<string> {
    try {
        // Fetch the current environment from our server-side endpoint
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

    // Handle API requests by forwarding to the backend
    if (event.url.pathname.startsWith('/api/') &&
        !event.url.pathname.startsWith('/api/environment/')) {

        try {
            console.log('event.url', event.url);
            const backendUrl = await getBackendUrl();
            const pathWithoutApi = event.url.pathname.replace(/^\/api/, '');
            const targetUrl = `${backendUrl}/api${pathWithoutApi}${event.url.search}`;

            console.log(`Proxying request to: ${targetUrl}`);

            // Forward the request to the backend
            const response = await fetch(targetUrl, {
                method: event.request.method,
                headers: event.request.headers,
                body: event.request.method !== 'GET' && event.request.method !== 'HEAD'
                    ? await event.request.clone().arrayBuffer()
                    : undefined,
                credentials: 'include'
            });

            // Copy all headers from the backend response
            const headers = new Headers();
            response.headers.forEach((value, key) => {
                headers.append(key, value);
            });

            // Add CORS headers if needed
            if (origin && ALLOWED_ORIGINS.includes(origin)) {
                headers.append('Access-Control-Allow-Origin', origin);
                headers.append('Access-Control-Allow-Credentials', 'true');
            }

            // Create a new response with the headers and body from the backend
            return new Response(response.body, {
                status: response.status,
                statusText: response.statusText,
                headers
            });
        } catch (error) {
            console.error('Error proxying request:', error);
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
