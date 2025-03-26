<script lang="ts">
    import { goto } from "$app/navigation";
    import * as auth from "$lib/stores/auth";

    let email = "";
    let password = "";
    let error = "";
    let loading = false;

    async function handleLogin() {
        if (!email || !password) {
            error = "Email and password are required";
            return;
        }

        loading = true;
        error = "";

        try {
            const response = await fetch("/api/auth/login", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ email, password }),
            });

            const data = await response.json();

            if (data.error) {
                error = data.error;
                return;
            }

            if (data.user) {
                // Update auth state with new user
                auth.setUser(data.user);
                // Redirect to home page or dashboard
                goto("/prop_firms/");
            } else {
                error = "Login failed - no user returned";
            }
        } catch (err) {
            console.error("Login error:", err);
            error =
                err instanceof Error ? err.message : "Unknown error occurred";
        } finally {
            loading = false;
        }
    }
</script>

<div class="max-w-md mx-auto mt-10 bg-white p-6 rounded-lg shadow-md">
    <h1 class="text-2xl font-bold mb-6 text-center">Login</h1>

    {#if error}
        <div
            class="bg-red-100 border-l-4 border-red-500 text-red-700 p-4 mb-4"
            role="alert"
        >
            <p>{error}</p>
        </div>
    {/if}

    <form onsubmit={handleLogin} class="space-y-4">
        <div>
            <label for="email" class="block text-sm font-medium text-gray-700"
                >Email</label
            >
            <input
                type="email"
                id="email"
                bind:value={email}
                class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                required
            />
        </div>

        <div>
            <label
                for="password"
                class="block text-sm font-medium text-gray-700">Password</label
            >
            <input
                type="password"
                id="password"
                bind:value={password}
                class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                required
            />
        </div>

        <div>
            <button
                type="submit"
                class="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                disabled={loading}
            >
                {loading ? "Logging in..." : "Login"}
            </button>
        </div>
    </form>

    <div class="mt-4 text-center">
        <p class="text-sm text-gray-600">
            Don't have an account? <a
                href="/register"
                class="text-blue-600 hover:underline">Register</a
            >
        </p>
    </div>
</div>
