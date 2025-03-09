// Router for the trades endpoint
import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { getBackendUrl } from '$lib/stores/environment';



export const GET: RequestHandler = async () => {
    const backendUrl = getBackendUrl();
    const response = await fetch(`${backendUrl}/trades`);
    const data = await response.json();
    return json(data);
};

