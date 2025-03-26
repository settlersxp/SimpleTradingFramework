import { redirect } from '@sveltejs/kit';

export const GET = async ({ cookies }) => {
    cookies.delete('user_id', { path: '/' });
    cookies.delete('session', { path: '/' });
    redirect(302, '/login');
};