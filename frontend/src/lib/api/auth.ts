import { getBackendUrl } from "$lib/stores/environment";

export interface User {
    id: number;
    email: string;
    created_at: string;
    updated_at: string;
    prop_firms: number[];
}

export interface AuthResponse {
    message: string;
    user?: User;
    error?: string;
}

export async function register(email: string, password: string): Promise<AuthResponse> {
    try {
        const response = await fetch(`${getBackendUrl()}/api/auth/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email, password }),
            credentials: 'include',
        });

        return await response.json();
    } catch (error) {
        return { message: 'Registration failed', error: error instanceof Error ? error.message : 'Unknown error' };
    }
}

export async function login(email: string, password: string): Promise<AuthResponse> {
    try {
        const response = await fetch(`${getBackendUrl()}/api/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email, password }),
            credentials: 'include',
        });

        return await response.json();
    } catch (error) {
        return { message: 'Login failed', error: error instanceof Error ? error.message : 'Unknown error' };
    }
}

export async function logout(): Promise<AuthResponse> {
    try {
        const response = await fetch(`${getBackendUrl()}/api/auth/logout`, {
            method: 'POST',
            credentials: 'include',
        });

        return await response.json();
    } catch (error) {
        return { message: 'Logout failed', error: error instanceof Error ? error.message : 'Unknown error' };
    }
}

export async function getCurrentUser(): Promise<AuthResponse> {
    try {
        const response = await fetch(`/api/auth/me`, {
            credentials: 'include',
        });

        return await response.json();
    } catch (error) {
        return { message: 'Failed to get user', error: error instanceof Error ? error.message : 'Unknown error' };
    }
}

export async function deleteUser(userId: number): Promise<AuthResponse> {
    try {
        const response = await fetch(`${getBackendUrl()}/api/auth/users/${userId}`, {
            method: 'DELETE',
            credentials: 'include',
        });

        return await response.json();
    } catch (error) {
        return { message: 'Failed to delete user', error: error instanceof Error ? error.message : 'Unknown error' };
    }
}
