import { getBackendUrl } from "$lib/stores/environment";
import type { AuthResponse } from "$lib/types/AuthResponse";

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
