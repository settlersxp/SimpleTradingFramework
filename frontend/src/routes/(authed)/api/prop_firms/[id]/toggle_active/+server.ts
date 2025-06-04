import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';

export const POST: RequestHandler = async ({ request, params, fetch }) => {
    const { id } = params;
    const { status } = await request.json();

    console.log("Toggling active for firm:", id, status);

    try {
        const response = await fetch(`/python/prop_firms/${id}`, {
            method: "PUT",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                'is_active': status,
            }),
        });

        if (!response.ok) {
            throw new Error("Failed to toggle active");
        }

        return response;
    } catch (error) {
        console.error("Error toggling active:", error);
        return json({ success: false }, { status: 500 });
    }
};