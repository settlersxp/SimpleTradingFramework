import { getBackendUrl } from "$lib/stores/environment";
import type { PropFirm } from './prop_firms';

export interface UserPropFirmsResponse {
    prop_firms?: PropFirm[];
    message?: string;
    error?: string;
}

export async function getUserPropFirms(): Promise<UserPropFirmsResponse> {
    try {
        const response = await fetch(`${getBackendUrl()}/api/user/prop_firms`, {
            credentials: 'include',
        });

        return await response.json();
    } catch (error) {
        return { error: error instanceof Error ? error.message : 'Unknown error' };
    }
}

export async function addPropFirmToUser(propFirmId: number): Promise<{ message: string; error?: string }> {
    try {
        const response = await fetch(`${getBackendUrl()}/api/user/prop_firms/${propFirmId}`, {
            method: 'POST',
            credentials: 'include',
        });

        return await response.json();
    } catch (error) {
        return { message: 'Failed to add prop firm', error: error instanceof Error ? error.message : 'Unknown error' };
    }
}

export async function removePropFirmFromUser(propFirmId: number): Promise<{ message: string; error?: string }> {
    try {
        const response = await fetch(`${getBackendUrl()}/api/user/prop_firms/${propFirmId}`, {
            method: 'DELETE',
            credentials: 'include',
        });

        return await response.json();
    } catch (error) {
        return { message: 'Failed to remove prop firm', error: error instanceof Error ? error.message : 'Unknown error' };
    }
}
