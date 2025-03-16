import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { getBackendUrl } from '$lib/stores/environment';

export const GET: RequestHandler = async ({ cookies, request }) => {
    try {
        // Get all cookies from the request to forward them to the backend
        const cookieHeader = request.headers.get('cookie');

        // Make request to backend
        const backendUrl = getBackendUrl();
        const response = await fetch(`${backendUrl}/api/auth/me`, {
            headers: {
                'Cookie': cookieHeader || '',
            },
            credentials: 'include',
        });

        if (!response.ok) {
            // If the backend returns an error, pass it through
            const errorData = await response.json();
            return json(errorData, { status: response.status });
        }

        // Return the user data
        const data = await response.json();
        return json(data);
    } catch (error) {
        console.error('Error fetching current user:', error);
        return json({
            message: 'Failed to get user',
            error: error instanceof Error ? error.message : 'Unknown error'
        }, { status: 500 });
    }
}; 