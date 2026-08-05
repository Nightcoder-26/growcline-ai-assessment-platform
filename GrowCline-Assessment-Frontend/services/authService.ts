/**
 * Auth Service
 * Wraps the shared Axios instance for login and registration.
 * Persists JWT token and user info to localStorage after successful login.
 */

import apiClient from "@/lib/apiClient";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface LoginPayload {
  email: string;
  password: string;
}

export interface RegisterPayload {
  fullName: string;
  email: string;
  password: string;
  role: "candidate" | "recruiter" | "admin";
}

export interface AuthUser {
  id: string;
  fullName: string;
  email: string;
  role: string;
}

export interface AuthResponse {
  success: boolean;
  message: string;
  token?: string;
  user?: AuthUser;
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

const TOKEN_KEY = "token";
const USER_KEY = "auth_user";

export function storeAuth(token: string, user: AuthUser) {
  if (typeof window === "undefined") return;
  localStorage.setItem(TOKEN_KEY, token);
  localStorage.setItem(USER_KEY, JSON.stringify(user));
}

export function clearAuth() {
  if (typeof window === "undefined") return;
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
}

export function getStoredUser(): AuthUser | null {
  if (typeof window === "undefined") return null;
  try {
    const raw = localStorage.getItem(USER_KEY);
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

export function getStoredToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(TOKEN_KEY);
}

// ---------------------------------------------------------------------------
// API calls
// ---------------------------------------------------------------------------

export async function login(payload: LoginPayload): Promise<AuthResponse> {
  const { data } = await apiClient.post<AuthResponse>("/api/auth/login", payload);

  if (data.token && data.user) {
    storeAuth(data.token, data.user);
  }

  return data;
}

export async function register(payload: RegisterPayload): Promise<AuthResponse> {
  const { data } = await apiClient.post<AuthResponse>("/api/auth/register", payload);
  return data;
}

export function logout() {
  clearAuth();
}
