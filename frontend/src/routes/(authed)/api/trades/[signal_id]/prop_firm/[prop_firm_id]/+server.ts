import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';

// Delete a trade
export const DELETE: RequestHandler = async ({ params, fetch }: { params: any, fetch: any }) => {
    const url = `/python/trades/${params.signal_id}/prop_firm/${params.prop_firm_id}`
    console.log("URL in API:", url);
    try {
        const response = await fetch(url, {
            method: 'DELETE'
        });

        console.log("Response:", response);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        // If the backend returns 204 No Content we cannot call response.json()
        if (response.status === 204) {
            return json({ message: 'Trade deleted successfully' });
        }

        const data = await response.json();
        return json(data);
    } catch (error) {
        console.error('Error deleting trade:', error);
        return json({ error: 'Failed to delete trade' }, { status: 500 });
    }
}; 