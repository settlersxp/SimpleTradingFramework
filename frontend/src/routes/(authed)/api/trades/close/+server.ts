import { json } from "@sveltejs/kit";

export const POST = async ({ request, fetch }: { request: any, fetch: any }) => {
    const { platform_id, prop_firm_id } = await request.json();
    const response = await fetch(`/python/trades/close`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            platform_id,
            prop_firm_id,
        }),
    });
    const data = await response.json();
    return json(data);
};
