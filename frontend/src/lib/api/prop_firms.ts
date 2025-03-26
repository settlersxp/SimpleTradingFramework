import { getBackendUrl } from "$lib/stores/environment";

export interface PropFirm {
    id: number;
    name: string;
    username: string;
    ip_address: string;
    port: number;
    platform_type: string;
    is_active: boolean;
    full_balance: number;
    available_balance: number;
    dowdown_percentage: number;
    created_at: string;
    updated_at: string;
}

export interface PropFirmsResponse {
    prop_firms?: PropFirm[];
    message?: string;
    error?: string;
}

export async function getAllPropFirms(): Promise<PropFirmsResponse> {
    try {
        const response = await fetch(`/python/prop_firms`, {
            credentials: 'include',
        });

        return await response.json();
    } catch (error) {
        return { error: error instanceof Error ? error.message : 'Unknown error' };
    }
}

export async function getPropFirm(id: number): Promise<{ prop_firm?: PropFirm; error?: string }> {
    try {
        const response = await fetch(`/python/prop_firms/${id}`, {
            credentials: 'include',
        });

        return await response.json();
    } catch (error) {
        return { error: error instanceof Error ? error.message : 'Unknown error' };
    }
}

export async function createPropFirm(propFirm: Omit<PropFirm, 'id' | 'created_at' | 'updated_at'>): Promise<{ prop_firm?: PropFirm; error?: string }> {
    try {
        const response = await fetch(`/python/prop_firms`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(propFirm),
            credentials: 'include',
        });

        return await response.json();
    } catch (error) {
        return { error: error instanceof Error ? error.message : 'Unknown error' };
    }
}

export async function updatePropFirm(id: number, propFirm: Partial<PropFirm>): Promise<{ prop_firm?: PropFirm; error?: string }> {
    try {
        const response = await fetch(`/python/prop_firms/${id}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(propFirm),
            credentials: 'include',
        });

        return await response.json();
    } catch (error) {
        return { error: error instanceof Error ? error.message : 'Unknown error' };
    }
}

export async function deletePropFirm(id: number): Promise<{ message?: string; error?: string }> {
    try {
        const response = await fetch(`/python/prop_firms/${id}`, {
            method: 'DELETE',
            credentials: 'include',
        });

        return await response.json();
    } catch (error) {
        return { error: error instanceof Error ? error.message : 'Unknown error' };
    }
}
