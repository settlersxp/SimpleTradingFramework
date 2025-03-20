import { redirect } from '@sveltejs/kit';

export async function load({ cookies, url }) {
    if (!cookies.get('session') || !cookies.get('user_id')) {
        throw redirect(303, `/login?redirectTo=${url.pathname}`);
    }

    return {};
}
