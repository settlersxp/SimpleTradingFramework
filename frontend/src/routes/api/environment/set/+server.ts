import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { env } from '$env/dynamic/private';

// Server-side storage for the current environment
// This will persist as long as the server is running
let currentEnvironment = env.VITE_INITIAL_ENVIRONMENT || 'local';

// Handle POST requests to update the environment
export const POST: RequestHandler = async ({ request }) => {
    try {
        const data = await request.json();
        if (data && data.environment) {
            // Update the server-side environment
            currentEnvironment = data.environment;
            console.log(`Server environment set to: ${currentEnvironment}`);

            return json({ success: true, environment: currentEnvironment });
        } else {
            return json({ success: false, error: 'Invalid environment data' }, { status: 400 });
        }
    } catch (error) {
        console.error('Error updating environment:', error);
        return json(
            { success: false, error: error instanceof Error ? error.message : 'Unknown error' },
            { status: 500 }
        );
    }
};

// Handle GET requests to retrieve the current environment
export const GET: RequestHandler = async () => {
    return json({ environment: currentEnvironment });
}; 