import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { getBackendUrl } from "$lib/stores/environment";

// Handle DELETE requests to /api/auth/logout
export const DELETE: RequestHandler = async ({ cookies }) => {
    try {
        const backendUrl = getBackendUrl();
        const response = await fetch(`${backendUrl}/api/auth/logout/${cookies.get('session')}_${cookies.get('user_id')}`, {
            method: 'DELETE',
            credentials: 'include',
        });

        const result = await response.json();

        // Delete our frontend cookie
        cookies.delete('user_id', { path: '/' });
        cookies.delete('session', { path: '/' });
        // Create response object
        const jsonResponse = json(result);

        // Forward any Flask session cookies (which should be cleared by logout)
        const setCookieHeaders = response.headers.getSetCookie();
        if (setCookieHeaders && setCookieHeaders.length > 0) {
            for (const cookieHeader of setCookieHeaders) {
                jsonResponse.headers.append('Set-Cookie', cookieHeader);
            }
        }

        return jsonResponse;
    } catch (error) {
        console.error('Logout error:', error);
        return json({
            message: 'Logout failed',
            error: error instanceof Error ? error.message : 'Unknown error'
        }, { status: 500 });
    }
}; 