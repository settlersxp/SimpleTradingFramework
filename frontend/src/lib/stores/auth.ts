import type { User } from '$lib/api/auth';
import { browser } from '$app/environment';

// User state using Svelte 5 runes
export let $user: User | null = null;
export let $isAuthenticated = false;
export let $isLoading = false;

// This function is called to initialize auth state from a server response
export function setUser(userData: User | null) {
    $user = userData;
    $isAuthenticated = !!userData;
    console.log('userData', userData);
}

// Initialize the store
export function initAuth() {
    if (browser && $user) {
        $isLoading = true;
        // Call our server endpoint which will respect cookies
        fetch('/api/auth/me')
            .then(response => response.json())
            .then(data => {
                if (data.user) {
                    setUser(data.user);
                } else {
                    setUser(null);
                }
            })
            .catch(err => {
                console.error('Error checking authentication:', err);
                setUser(null);
            })
            .finally(() => {
                $isLoading = false;
            });

    }
}
