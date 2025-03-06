import type { Handle } from '@sveltejs/kit';

const ALLOWED_ORIGINS = [
    'http://localhost:5173',
    'http://localhost:3100',
    'http://100.66.179.48:3100',
    // Add other allowed domains
];

export const handle: Handle = async ({ event, resolve }) => {
    const origin = event.request.headers.get('origin');

    // Handle preflight requests
    if (event.request.method === 'OPTIONS') {
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

    const response = await resolve(event);

    // Add CORS headers to all responses
    if (origin && ALLOWED_ORIGINS.includes(origin)) {
        response.headers.append('Access-Control-Allow-Origin', origin);
        response.headers.append('Access-Control-Allow-Credentials', 'true');
    }

    return response;
};
