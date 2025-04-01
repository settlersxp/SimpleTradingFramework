import type { Actions, RequestEvent } from "@sveltejs/kit";

// Form Actions
export const actions: Actions = {
    create: async ({ request, fetch }: RequestEvent) => {
        const formData = await request.formData();
        const name = formData.get("name") as string;
        const description = formData.get("description") as string || null;

        if (!name || !name.trim()) {
            return { success: false, error: "Strategy name is required" };
        }

        try {
            const response = await fetch("/api/trading_strategies", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ name, description }),
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({ error: "Failed to create strategy" }));
                return { success: false, error: errorData.error || "Failed to create strategy" };
            }

            return { success: true };
        } catch (err) {
            console.error("Error creating strategy:", err);
            if (err instanceof Error) {
                return { success: false, error: err.message };
            } else {
                return { success: false, error: "An unknown error occurred during creation." };
            }
        }
    },

    update: async ({ request, fetch }: RequestEvent) => {
        const formData = await request.formData();
        const id = formData.get("id") as string;
        const name = formData.get("name") as string;
        const description = formData.get("description") as string || null;

        if (!id) {
            return { success: false, error: "Strategy ID is missing" };
        }
        if (!name || !name.trim()) {
            return { success: false, error: "Strategy name is required" };
        }

        try {
            const response = await fetch(`/api/trading_strategies/${id}`, {
                method: "PUT",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ name, description }),
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({ error: "Failed to update strategy" }));
                return { success: false, error: errorData.error || "Failed to update strategy" };
            }

            return { success: true };
        } catch (err) {
            console.error("Error updating strategy:", err);
            if (err instanceof Error) {
                return { success: false, error: err.message };
            } else {
                return { success: false, error: "An unknown error occurred during update." };
            }
        }
    },

    delete: async ({ request, fetch }: RequestEvent) => {
        const formData = await request.formData();
        const id = formData.get("id") as string;

        if (!id) {
            return { success: false, error: "Strategy ID is missing" };
        }

        try {
            const response = await fetch(`/api/trading_strategies/${id}`, {
                method: "DELETE",
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({ error: "Failed to delete strategy" }));
                return { success: false, error: errorData.error || "Failed to delete strategy" };
            }

            return { success: true };
        } catch (err) {
            console.error("Error deleting strategy:", err);
            if (err instanceof Error) {
                return { success: false, error: err.message };
            } else {
                return { success: false, error: "An unknown error occurred during deletion." };
            }
        }
    },
}; 