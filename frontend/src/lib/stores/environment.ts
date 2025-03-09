import { writable } from 'svelte/store';
import { browser } from '$app/environment';

// Function to dynamically load environment config
async function loadEnvironmentConfig(env) {
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
export const environments = {};

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
    });
}

// Helper function to get the current backend URL
export function getBackendUrl() {
    let env;
    selectedEnvironment.subscribe(value => {
        env = value;
    })();

    return environments[env]?.backendUrl || 'http://localhost:3100'; // Fallback
} 