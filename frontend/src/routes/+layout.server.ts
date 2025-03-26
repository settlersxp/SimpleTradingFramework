import type { LayoutServerLoad } from './$types';
import type { User } from '$lib/api/auth';

export const load: LayoutServerLoad = async ({ cookies, fetch }) => {
    // Get cookies that were set in the login route
    const userId = cookies.get('user_id');
    const sessionToken = cookies.get('session');

    if (!userId || !sessionToken) {
        return {
            user: null
        };
    }

    try {
        const meUrl = `/python/auth/me/${sessionToken}_${userId}`;
        console.log('meUrl', meUrl);

        const response = await fetch(meUrl, {
            credentials: 'include',
            headers: {
                'Cookie': `session=${sessionToken}; user_id=${userId}`
            }
        });

        if (!response.ok) {
            return { user: null };
        }

        const data = await response.json();

        if (data.user) {
            // Successfully loaded user from API
            return {
                user: data.user as User
            };
        }

        return { user: null };
    } catch (error) {
        console.error('Error loading user in layout server:', error);
        return { user: null };
    }
};
