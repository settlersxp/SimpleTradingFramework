import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { getBackendUrl } from "$lib/stores/environment";
import type { AuthResponse } from "$lib/api/auth";

// Handle POST requests to /api/auth/register
export const POST: RequestHandler = async ({ request }) => {
    try {
        const data = await request.json();
        const { email, password } = data;

        if (!email || !password) {
            return json({
                message: 'Registration failed',
                error: 'Email and password are required'
            }, { status: 400 });
        }

        const response = await register(email, password);

        if (response.error) {
            return json(response, { status: 400 });
        }

        return json(response);
    } catch (error) {
        console.error('Registration error:', error);
        return json({
            message: 'Registration failed',
            error: error instanceof Error ? error.message : 'Unknown error'
        }, { status: 500 });
    }
};

async function register(email: string, password: string): Promise<AuthResponse> {
    try {
        const backendUrl = getBackendUrl();
        console.log(`Registering user at ${backendUrl}/api/auth/register`);

        const response = await fetch(`${backendUrl}/api/auth/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email, password }),
            credentials: 'include',
        });

        const result = await response.json();

        if (!response.ok) {
            return {
                message: 'Registration failed',
                error: result.error || `Server responded with status: ${response.status}`
            };
        }

        return result;
    } catch (error) {
        console.error('Registration fetch error:', error);
        return {
            message: 'Registration failed',
            error: error instanceof Error ? error.message : 'Unknown error'
        };
    }
} 