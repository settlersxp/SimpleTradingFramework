import { redirect } from '@sveltejs/kit';
import { getBackendUrl } from '$lib/stores/environment';

export async function load({ url }) {
    try {
        const response = await fetch(`${getBackendUrl()}/api/auth/me`, {
            credentials: 'include'
        });

        const data = await response.json();

        if (data.user) {
            throw redirect(303, '/prop_firms');
        }

        return {};
    } catch (error) {
        // If fetch fails, user is not logged in, so allow access
        return {};
    }
}
