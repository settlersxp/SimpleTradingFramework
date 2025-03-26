import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { dev } from '$app/environment';


// Handle POST requests to /python/auth/login
export const POST: RequestHandler = async ({ request, cookies, fetch }: { request: any, cookies: any, fetch: any }) => {
    const request_data = await request.json();
    const { email, password } = request_data;

    if (!email || !password) {
        return json({
            message: 'Login failed',
            error: 'Email and password are required'
        }, { status: 400 });
    }

    try {
        const loginUrl = `/python/auth/login`;
        console.log(`Logging in at ${loginUrl}`);

        const response = await fetch(loginUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email, password }),
            credentials: 'include', // Important to include credentials to get and set cookies
        });

        const result = await response.json();

        if (result.error) {
            return json(result, { status: 400 });
        }

        console.log('result', result);
        // If login was successful and we have a user, set user_id cookie for frontend use
        if (result.user?.id) {
            // Set user_id cookie for client-side identification
            cookies.set('user_id', String(result.user.id), {
                path: '/',
                httpOnly: true,
                secure: !dev,
                sameSite: 'lax',
                maxAge: 60 * 60 * 24 * 7 // 1 week
            });

            // Set session token for auth validation
            cookies.set('session', result.user.token, {
                path: '/',
                httpOnly: true,
                secure: !dev,
                sameSite: 'lax',
                maxAge: 60 * 60 * 24 * 7 // 1 week
            });

            // Make sure the user property is properly structured
            if (!result.user.hasOwnProperty('email') && result.user.hasOwnProperty('username')) {
                result.user.email = result.user.username;
            }
        }

        // Create a successful response
        const jsonResponse = json(result);

        // Forward any Flask session cookies from the backend response
        const setCookieHeaders = response.headers.getSetCookie();
        if (setCookieHeaders && setCookieHeaders.length > 0) {
            for (const cookieHeader of setCookieHeaders) {
                jsonResponse.headers.append('Set-Cookie', cookieHeader);
            }
        }

        return jsonResponse;
    } catch (error) {
        console.error('Login error:', error);
        return json({
            message: 'Login failed',
            error: error instanceof Error ? error.message : 'Unknown error'
        }, { status: 500 });
    }
};