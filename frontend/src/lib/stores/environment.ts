import { writable } from 'svelte/store';
import { browser } from '$app/environment';

// Interface for environment config
interface EnvironmentConfig {
    name: string;
    backendUrl: string;
    apiTimeout: number;
    enableDebug: boolean;
    [key: string]: any; // Allow for additional properties
}

// Interface for environments object
interface Environments {
    [key: string]: EnvironmentConfig;
}

// Function to dynamically load environment config
async function loadEnvironmentConfig(env: string): Promise<EnvironmentConfig | null> {
    try {
        const module = await import(`$lib/config/${env}.js`);
        return {
            name: env.charAt(0).toUpperCase() + env.slice(1),
            ...module.default
        };
    } catch (error) {
        console.error(`Failed to load config for environment: ${env}`, error);
        return null;
    }
}

// Available environments
const availableEnvironments = ['local', 'production'];

// Initialize the environments object
export const environments: Environments = {};

// Initialize from localStorage if available, otherwise default to 'local'
const storedEnv = browser && localStorage.getItem('selectedEnvironment');
const initialEnv = storedEnv && availableEnvironments.includes(storedEnv)
    ? storedEnv
    : 'local';

// Create the store
export const selectedEnvironment = writable(initialEnv);
export const environmentsLoaded = writable(false);

// Load all environment configurations
if (browser) {
    Promise.all(
        availableEnvironments.map(async (env) => {
            const config = await loadEnvironmentConfig(env);
            console.log(config);
            if (config) {
                environments[env] = config;
            }
        })
    ).then(() => {
        environmentsLoaded.set(true);
    });

    // Update localStorage when the environment changes
    selectedEnvironment.subscribe(value => {
        localStorage.setItem('selectedEnvironment', value);

        // Notify the server about environment change
        updateServerEnvironment(value);
    });
}

// Helper function to get the current backend URL
export function getBackendUrl(): string {
    let env: string = 'local'; // Default to local
    selectedEnvironment.subscribe(value => {
        env = value;
    })();

    return environments[env]?.backendUrl || 'http://localhost:3100'; // Fallback
}

// Function to update the server-side environment setting
async function updateServerEnvironment(env: string): Promise<void> {
    try {
        await fetch('/api/environment/set', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ environment: env })
        });
        console.log(`Server environment updated to: ${env}`);
    } catch (error) {
        console.error('Failed to update server environment:', error);
    }
} 