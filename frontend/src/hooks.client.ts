import { initAuth } from '$lib/stores/auth';
import type { HandleClientError } from '@sveltejs/kit';

// Initialize authentication when the client-side app loads
initAuth();

// Handle client errors (optional)
export const handleError: HandleClientError = ({ error, event }) => {
    console.error('Client error:', error);

    return {
        message: 'An unexpected error occurred',
        code: (error as any)?.code ?? 'UNKNOWN'
    };
}; 