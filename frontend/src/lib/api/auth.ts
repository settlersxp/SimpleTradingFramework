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
    cookies?: string[];
}

export async function logout(): Promise<AuthResponse> {
    try {
        const response = await fetch(`/api/auth/logout`, {
            method: 'DELETE',
        });

        return await response.json();
    } catch (error) {
        return { message: 'Logout failed', error: error instanceof Error ? error.message : 'Unknown error' };
    }
}

export async function getCurrentUser(): Promise<AuthResponse> {
    try {
        console.log('getting current user');
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
