import type { PageLoad } from './$types';

export const load: PageLoad = async ({ fetch, params }) => {
    const response = await fetch(`/api/prop_firms/${params.id}/trade_pairs`);

    if (!response.ok) {
        throw new Error('Failed to load trade pairs');
    }

    return await response.json();
}; 