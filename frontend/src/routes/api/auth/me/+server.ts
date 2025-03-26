import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { getBackendUrl } from '$lib/stores/environment';
import { dev } from '$app/environment';

// Handler for GET requests to /api/auth/me
export const GET: RequestHandler = async ({ cookies }) => {
    try {
        const backendUrl = getBackendUrl();

        console.log('auth me cookies', cookies.get('session'), cookies.get('user_id'));
        // Send request with credentials to include session cookies from Flask

        const response = await fetch(`${backendUrl}/auth/me/${cookies.get('session')}_${cookies.get('user_id')}`, {
            credentials: 'include',
        });

        if (!response.ok) {
            // If authentication fails, clear the frontend cookie
            cookies.delete('user_id', { path: '/' });
            return json({ message: 'Not authenticated' }, { status: 401 });
        }

        const result = await response.json();

        // If we get a successful response but don't have the user_id cookie set yet,
        // let's set it for frontend usage based on the user returned from backend
        if (result.user?.id && !cookies.get('user_id')) {
            cookies.set('user_id', String(result.user.id), {
                path: '/',
                httpOnly: true,
                secure: !dev,
                sameSite: 'lax',
                maxAge: 60 * 60 * 24 * 7 // 1 week
            });
        }

        return json(result);
    } catch (error) {
        console.error('Authentication check error:', error);
        return json({
            message: 'Failed to get user information',
            error: error instanceof Error ? error.message : 'Unknown error'
        }, { status: 500 });
    }
};