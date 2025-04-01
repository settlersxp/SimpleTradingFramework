import type { User } from "./User";

export interface AuthResponse {
    message: string;
    user?: User;
    error?: string;
    cookies?: string[];
}