import type { User } from "$lib/types/User";

// User state using Svelte 5 runes
export let $user: User | null = null;
export let $isAuthenticated = false;
// Keep isLoading if you have other async operations, otherwise consider removing
export let $isLoading = false;

// This function is called to initialize auth state from a server response
export function setUser(userData: User | null) {
    $user = userData;
    $isAuthenticated = !!userData;
    $isLoading = false; // Explicitly set isLoading to false here
    // Optional: remove console.log in production
    console.log('setUser called with:', userData);
    // Add log to see the state immediately after setting
    console.log('auth.$user is now:', $user);
    console.log('auth.$isLoading is now:', $isLoading);
}
