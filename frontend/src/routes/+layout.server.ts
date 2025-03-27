import type { LayoutServerLoad } from './$types';
import type { User } from '$lib/api/auth';

export const load: LayoutServerLoad = async ({ cookies, fetch }) => {
    const userId = cookies.get('user_id');
    const sessionToken = cookies.get('session');

    if (!userId || !sessionToken) {
        // No cookies, definitely no user
        return { user: null };
    }

    // If cookies exist, try fetching the user data
    try {
        // Correct URL - no trailing slash
        const meUrl = `/python/auth/me`;
        console.log('Fetching user data from:', meUrl); // Log the correct URL

        // Make the fetch call *without* manually setting Cookie or Auth headers.
        // The server hook (hooks.server.ts) will intercept '/python/',
        // read the 'session' and 'user_id' cookies from the incoming request context,
        // and add the required 'X-Session-ID' and 'X-User-ID' headers.
        const response = await fetch(meUrl); // Removed headers and credentials options

        if (!response.ok) {
            // Log status if fetch failed
            console.error(`Failed to fetch user data from ${meUrl}. Status: ${response.status}`);
            // Optionally clear cookies if auth failed (e.g., 401 Unauthorized)
            if (response.status === 401 || response.status === 400) {
                cookies.delete('session', { path: '/' });
                cookies.delete('user_id', { path: '/' });
            }
            return { user: null };
        }

        const data = await response.json();

        if (data.user) {
            console.log('Successfully loaded user:', data.user.id); // Log success
            return { user: data.user as User };
        } else {
            console.log('API response did not contain user data.');
            return { user: null };
        }

    } catch (error) {
        console.error('Error in root layout server load fetching user:', error);
        return { user: null };
    }
};
