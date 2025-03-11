import { redirect } from '@sveltejs/kit';
import { getBackendUrl } from '$lib/stores/environment';

export async function load({ cookies, url }) {
    try {
        const response = await fetch(`${getBackendUrl()}/api/auth/me`, {
            credentials: 'include'
        });

        const data = await response.json();

        if (!data.user) {
            throw redirect(303, `/login?redirectTo=${url.pathname}`);
        }

        return {
            user: data.user
        };
    } catch (error) {
        throw redirect(303, `/login?redirectTo=${url.pathname}`);
    }
}
