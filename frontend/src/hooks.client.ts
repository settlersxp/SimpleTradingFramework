import type { HandleClientError } from '@sveltejs/kit';

// Handle client errors (optional)
export const handleError: HandleClientError = ({ error, event }) => {
    console.error('Client error:', error);

    return {
        message: 'An unexpected error occurred',
        code: (error as any)?.code ?? 'UNKNOWN'
    };
}; 