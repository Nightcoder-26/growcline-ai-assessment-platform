/**
 * useAuth — reads JWT auth state from localStorage.
 *
 * Team A's login page stores the JWT under "token" and the user payload
 * is a standard base64-encoded JWT with { id, email, role } claims.
 *
 * Usage:
 *   const { token, userId, role, isAuthenticated } = useAuth();
 */

"use client";

import { useEffect, useState } from "react";

export interface AuthState {
  token: string | null;
  userId: string | null;
  email: string | null;
  role: string | null;
  isAuthenticated: boolean;
}

// ---------------------------------------------------------------------------
// Helper — safely decode JWT payload without a library
// ---------------------------------------------------------------------------

function decodeJwtPayload(token: string): Record<string, unknown> | null {
  try {
    const parts = token.split(".");
    if (parts.length !== 3) return null;
    // Replace URL-safe base64 chars and pad
    const base64 = parts[1].replace(/-/g, "+").replace(/_/g, "/");
    const padded = base64 + "=".repeat((4 - (base64.length % 4)) % 4);
    return JSON.parse(atob(padded));
  } catch {
    return null;
  }
}

// ---------------------------------------------------------------------------
// Hook
// ---------------------------------------------------------------------------

export function useAuth(): AuthState {
  const [authState, setAuthState] = useState<AuthState>({
    token: null,
    userId: null,
    email: null,
    role: null,
    isAuthenticated: false,
  });

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) {
      setAuthState({
        token: null,
        userId: null,
        email: null,
        role: null,
        isAuthenticated: false,
      });
      return;
    }

    const payload = decodeJwtPayload(token);

    setAuthState({
      token,
      userId: (payload?.id as string) ?? (payload?.sub as string) ?? null,
      email: (payload?.email as string) ?? null,
      role: (payload?.role as string) ?? null,
      isAuthenticated: true,
    });
  }, []);

  return authState;
}
