import { writable } from 'svelte/store';
import type { User } from '$lib/api/auth';
import { browser } from '$app/environment';
import { getBackendUrl } from "$lib/stores/environment";

export const user = writable<User | null>(null);
export const isAuthenticated = writable<boolean>(false);
export const isLoading = writable<boolean>(true);

// Initialize the store
export function initAuth() {
    if (browser) {
        isLoading.set(true);
        fetch(`${getBackendUrl()}/api/auth/me`, {
            credentials: 'include',
        })
            .then(res => res.json())
            .then(data => {
                if (data.user) {
                    user.set(data.user);
                    isAuthenticated.set(true);
                } else {
                    user.set(null);
                    isAuthenticated.set(false);
                }
            })
            .catch(() => {
                user.set(null);
                isAuthenticated.set(false);
            })
            .finally(() => {
                isLoading.set(false);
            });
    }
}
