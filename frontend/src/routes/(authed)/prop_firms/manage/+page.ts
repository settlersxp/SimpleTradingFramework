import type { PageLoad } from './$types';

// Assuming types are accessible, e.g., from a shared types file
import type { PropFirm, PropFirmData } from '../../../../lib/types/PropFirms';

export const load: PageLoad = async ({ fetch: skFetch }) => { // Use the fetch provided by PageLoad
    let userPropFirms: any[] = []; // Use 'any' or import PropFirm type
    let allPropFirms: any[] = []; // Use 'any' or import PropFirm type
    let error: string | null = null;

    try {
        // Load user's prop firms via the SvelteKit endpoint GET /prop_firms/manage?user=true
        const userResponse = await skFetch('/api/prop_firms/manage?user=true');
        const userData = await userResponse.json();

        if (!userResponse.ok) {
            // Use error message from SvelteKit endpoint response body
            error = userData.message || `Failed to load user prop firms (Status: ${userResponse.status})`;
        } else {
            // The Python API returns { prop_firms: [...] }, which our GET handler passes through
            userPropFirms = userData.prop_firms || [];
        }

        // Load all prop firms only if user firms loaded successfully
        if (!error) {
            // Load all prop firms via the SvelteKit endpoint GET /prop_firms/manage
            const allResponse = await skFetch('/api/prop_firms/manage');
            const allData = await allResponse.json();

            if (!allResponse.ok) {
                error = allData.message || `Failed to load all prop firms (Status: ${allResponse.status})`;
            } else {
                // The Python API returns PropFirm[], which our GET handler passes through
                allPropFirms = allData || [];
            }
        }
    } catch (err: any) {
        error = 'Client-side error during data loading.'; // More specific client error
        console.error("Error in +page.ts load fetch:", err);
        // Avoid leaking potentially sensitive details from raw fetch errors
    }

    return {
        userPropFirms,
        allPropFirms,
        error,
        // Ensure types match what the component expects, cast if necessary
    };
};
