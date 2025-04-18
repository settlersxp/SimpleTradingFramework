<script lang="ts">
    import { goto } from "$app/navigation";

    let email = "";
    let password = "";
    let confirmPassword = "";
    let error = "";
    let isSubmitting = false;

    async function handleSubmit(event: Event) {
        event.preventDefault();
        error = "";

        // Validate form
        if (!email || !password || !confirmPassword) {
            error = "All fields are required";
            return;
        }

        if (password !== confirmPassword) {
            error = "Passwords do not match";
            return;
        }

        isSubmitting = true;

        try {
            const response = await fetch("/api/auth/register", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ email, password }),
            });

            const data = await response.json();

            if (!response.ok) {
                error = data.error || "Registration failed";
                isSubmitting = false;
                return;
            }

            // Success - redirect to login page
            goto("/login");
        } catch (e) {
            console.error("Registration error:", e);
            error =
                e instanceof Error ? e.message : "An unexpected error occurred";
            isSubmitting = false;
        }
    }
</script>

<svelte:head>
    <title>Register - Trading App</title>
</svelte:head>

<!-- Title slot for the layout -->
<slot slot="title">Create your account</slot>

<form class="space-y-6" onsubmit={handleSubmit}>
    {#if error}
        <div class="rounded-md bg-red-50 p-4">
            <div class="flex">
                <div class="ml-3">
                    <h3 class="text-sm font-medium text-red-800">{error}</h3>
                </div>
            </div>
        </div>
    {/if}

    <div>
        <label for="email" class="block text-sm font-medium text-gray-700">
            Email address
        </label>
        <div class="mt-1">
            <input
                id="email"
                name="email"
                type="email"
                autocomplete="email"
                required
                bind:value={email}
                class="block w-full appearance-none rounded-md border border-gray-300 px-3 py-2 placeholder-gray-400 shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-indigo-500 sm:text-sm"
            />
        </div>
    </div>

    <div>
        <label for="password" class="block text-sm font-medium text-gray-700">
            Password
        </label>
        <div class="mt-1">
            <input
                id="password"
                name="password"
                type="password"
                autocomplete="new-password"
                required
                bind:value={password}
                class="block w-full appearance-none rounded-md border border-gray-300 px-3 py-2 placeholder-gray-400 shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-indigo-500 sm:text-sm"
            />
        </div>
    </div>

    <div>
        <label
            for="confirm-password"
            class="block text-sm font-medium text-gray-700"
        >
            Confirm Password
        </label>
        <div class="mt-1">
            <input
                id="confirm-password"
                name="confirm-password"
                type="password"
                required
                bind:value={confirmPassword}
                class="block w-full appearance-none rounded-md border border-gray-300 px-3 py-2 placeholder-gray-400 shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-indigo-500 sm:text-sm"
            />
        </div>
    </div>

    <div>
        <button
            type="submit"
            disabled={isSubmitting}
            class="flex w-full justify-center rounded-md border border-transparent bg-indigo-600 py-2 px-4 text-sm font-medium text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 disabled:opacity-50 mt-4"
        >
            {#if isSubmitting}
                <svg
                    class="animate-spin -ml-1 mr-3 h-5 w-5 text-white"
                    xmlns="http://www.w3.org/2000/svg"
                    fill="none"
                    viewBox="0 0 24 24"
                >
                    <circle
                        class="opacity-25"
                        cx="12"
                        cy="12"
                        r="10"
                        stroke="currentColor"
                        stroke-width="4"
                    />
                    <path
                        class="opacity-75"
                        fill="currentColor"
                        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                    />
                </svg>
                Creating account...
            {:else}
                Create account
            {/if}
        </button>
    </div>
</form>

<div class="mt-6">
    <div class="relative">
        <div class="absolute inset-0 flex items-center">
            <div
                class="w-full border-t border-gray-300"
                style="border-color: #e5e7eb"
            ></div>
        </div>
        <div class="relative flex justify-center text-sm">
            <span class="bg-white px-2 text-gray-500">
                Already have an account?
            </span>
        </div>
    </div>

    <div class="mt-6">
        <a
            href="/login"
            class="flex w-full justify-center rounded-md border border-gray-300 bg-white py-2 px-4 text-sm font-medium text-gray-500 shadow-sm hover:bg-gray-50"
        >
            Sign in
        </a>
    </div>
</div>
