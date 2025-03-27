import { redirect } from '@sveltejs/kit';
import type { LayoutServerLoad } from './$types';

export const load: LayoutServerLoad = async ({ cookies, url, parent }) => {
    if (!cookies.get('session') || !cookies.get('user_id')) {
        throw redirect(303, `/login?redirectTo=${url.pathname}`);
    }

    const parentData = await parent();

    return {
        user: parentData.user
    };
};
