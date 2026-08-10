"use client";

/**
 * LoginForm — Full login form with validation, show/hide password,
 * remember-me, Google SSO button (UI only), and backend integration.
 */

import { useState, useId } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import {
  Eye, EyeOff, Mail, Lock, ArrowRight, Loader2,
  AlertCircle, Globe2,
} from "lucide-react";
import { login } from "@/services/authService";
import { getResumeStatus } from "@/services/resumeService";

// ─── Validation ────────────────────────────────────────────────────────────────
interface FormErrors {
  email?: string;
  password?: string;
  general?: string;
}

function validateForm(email: string, password: string): FormErrors {
  const errors: FormErrors = {};

  if (!email.trim()) {
    errors.email = "Email is required.";
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    errors.email = "Please enter a valid email address.";
  }

  if (!password) {
    errors.password = "Password is required.";
  } else if (password.length < 6) {
    errors.password = "Password must be at least 6 characters.";
  }

  return errors;
}

// ─── Field Component ───────────────────────────────────────────────────────────
function Field({
  id,
  label,
  error,
  children,
}: {
  id: string;
  label: string;
  error?: string;
  children: React.ReactNode;
}) {
  return (
    <div className="space-y-1.5">
      <label
        htmlFor={id}
        className="block text-[13px] font-semibold text-[#1E293B]"
      >
        {label}
      </label>
      {children}
      {error && (
        <p className="flex items-center gap-1.5 text-[12px] text-[#EF4444] font-medium">
          <AlertCircle size={12} />
          {error}
        </p>
      )}
    </div>
  );
}

// ─── Input Component ───────────────────────────────────────────────────────────
function Input({
  id,
  type,
  placeholder,
  value,
  onChange,
  hasError,
  icon: Icon,
  rightSlot,
  autoComplete,
}: {
  id: string;
  type: string;
  placeholder: string;
  value: string;
  onChange: (v: string) => void;
  hasError?: boolean;
  icon: React.ElementType;
  rightSlot?: React.ReactNode;
  autoComplete?: string;
}) {
  return (
    <div className="relative">
      <div className="absolute left-3.5 top-1/2 -translate-y-1/2 pointer-events-none">
        <Icon size={16} className={hasError ? "text-[#EF4444]" : "text-[#94A3B8]"} />
      </div>
      <input
        id={id}
        type={type}
        value={value}
        placeholder={placeholder}
        autoComplete={autoComplete}
        onChange={(e) => onChange(e.target.value)}
        className={`w-full h-[46px] pl-10 pr-${rightSlot ? "12" : "4"} bg-white border rounded-[11px] text-[14px] text-[#1E293B] placeholder-[#CBD5E1] outline-none transition-all
          ${
            hasError
              ? "border-[#EF4444] focus:border-[#EF4444] focus:ring-2 focus:ring-[#EF4444]/20"
              : "border-[rgba(30,41,59,0.14)] focus:border-[#4096FF] focus:ring-2 focus:ring-[#4096FF]/15"
          }
        `}
        style={{ paddingRight: rightSlot ? "3rem" : "1rem" }}
      />
      {rightSlot && (
        <div className="absolute right-3.5 top-1/2 -translate-y-1/2">{rightSlot}</div>
      )}
    </div>
  );
}

// ─── Divider ───────────────────────────────────────────────────────────────────
function Divider() {
  return (
    <div className="flex items-center gap-3 my-5">
      <div className="flex-1 h-px bg-[rgba(30,41,59,0.08)]" />
      <span className="text-[12px] text-[#94A3B8] font-medium">or continue with</span>
      <div className="flex-1 h-px bg-[rgba(30,41,59,0.08)]" />
    </div>
  );
}

// ─── LoginForm ─────────────────────────────────────────────────────────────────
export default function LoginForm() {
  const router = useRouter();
  const uid = useId();

  const [email, setEmail]           = useState("");
  const [password, setPassword]     = useState("");
  const [showPass, setShowPass]     = useState(false);
  const [rememberMe, setRememberMe] = useState(false);
  const [errors, setErrors]         = useState<FormErrors>({});
  const [loading, setLoading]       = useState(false);
  const [successMsg, setSuccessMsg] = useState("");

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setSuccessMsg("");

    const errs = validateForm(email, password);
    setErrors(errs);
    if (Object.keys(errs).length > 0) return;

    setLoading(true);
    try {
      await login({ email: email.trim(), password });
      setSuccessMsg("Login successful! Checking resume...");
      try {
        const status = await getResumeStatus();
        if (status.hasResume) {
          router.push("/dashboard");
        } else {
          router.push("/resume-onboarding");
        }
      } catch {
        router.push("/dashboard");
      }
    } catch (err: unknown) {
      const message =
        err instanceof Error ? err.message : "Invalid credentials. Please try again.";
      setErrors({ general: message });
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-[28px] font-extrabold text-[#1E293B] tracking-[-0.03em] leading-tight">
          Welcome back 👋
        </h1>
        <p className="mt-1.5 text-[14px] text-[#64748B]">
          Sign in to your GrowCline account.
        </p>
      </div>

      {/* General error / success */}
      {errors.general && (
        <div className="flex items-start gap-2.5 px-4 py-3 rounded-[11px] bg-[#FEF2F2] border border-[#FECACA] text-[13px] text-[#B91C1C]">
          <AlertCircle size={15} className="shrink-0 mt-0.5" />
          {errors.general}
        </div>
      )}
      {successMsg && (
        <div className="flex items-center gap-2.5 px-4 py-3 rounded-[11px] bg-[#F0FDF4] border border-[#86EFAC] text-[13px] text-[#15803D] font-medium">
          {successMsg}
        </div>
      )}

      <form onSubmit={handleSubmit} noValidate className="space-y-4">
        {/* Email */}
        <Field id={`${uid}-email`} label="Email address" error={errors.email}>
          <Input
            id={`${uid}-email`}
            type="email"
            placeholder="you@company.com"
            value={email}
            onChange={setEmail}
            hasError={!!errors.email}
            icon={Mail}
            autoComplete="email"
          />
        </Field>

        {/* Password */}
        <Field id={`${uid}-password`} label="Password" error={errors.password}>
          <Input
            id={`${uid}-password`}
            type={showPass ? "text" : "password"}
            placeholder="••••••••"
            value={password}
            onChange={setPassword}
            hasError={!!errors.password}
            icon={Lock}
            autoComplete="current-password"
            rightSlot={
              <button
                type="button"
                onClick={() => setShowPass((p) => !p)}
                className="text-[#94A3B8] hover:text-[#64748B] transition-colors"
                aria-label={showPass ? "Hide password" : "Show password"}
              >
                {showPass ? <EyeOff size={16} /> : <Eye size={16} />}
              </button>
            }
          />
        </Field>

        {/* Remember + Forgot */}
        <div className="flex items-center justify-between pt-0.5">
          <label className="flex items-center gap-2 cursor-pointer select-none">
            <input
              id={`${uid}-remember`}
              type="checkbox"
              checked={rememberMe}
              onChange={(e) => setRememberMe(e.target.checked)}
              className="w-4 h-4 rounded border-[rgba(30,41,59,0.25)] accent-[#4096FF]"
            />
            <span className="text-[13px] text-[#64748B]">Remember me</span>
          </label>
          <Link
            href="/forgot-password"
            className="text-[13px] text-[#4096FF] hover:text-[#3580eb] font-medium transition-colors"
          >
            Forgot password?
          </Link>
        </div>

        {/* Submit */}
        <button
          type="submit"
          disabled={loading}
          id="login-submit-btn"
          className="w-full h-[48px] flex items-center justify-center gap-2 rounded-[11px] bg-[#4096FF] hover:bg-[#3580eb] disabled:opacity-70 disabled:cursor-not-allowed text-white text-[14.5px] font-semibold transition-all shadow-[0_4px_18px_rgba(64,150,255,0.42)] hover:shadow-[0_6px_28px_rgba(64,150,255,0.54)] hover:-translate-y-px active:translate-y-0 mt-2"
        >
          {loading ? (
            <Loader2 size={18} className="animate-spin" />
          ) : (
            <>
              Sign In <ArrowRight size={15} />
            </>
          )}
        </button>
      </form>

      {/* Divider */}
      <Divider />

      {/* Google SSO (UI only) */}
      <button
        type="button"
        id="google-login-btn"
        className="w-full h-[46px] flex items-center justify-center gap-2.5 rounded-[11px] bg-white border border-[rgba(30,41,59,0.14)] text-[#1E293B] text-[14px] font-semibold hover:bg-[#F8FAFC] hover:border-[rgba(30,41,59,0.22)] transition-all shadow-sm hover:shadow-md"
      >
        <Globe2 size={18} className="text-[#4096FF]" />
        Continue with Google
      </button>

      {/* Sign up link */}
      <p className="text-center text-[13.5px] text-[#64748B]">
        Don&apos;t have an account?{" "}
        <Link
          href="/signup"
          className="text-[#4096FF] hover:text-[#3580eb] font-semibold transition-colors"
        >
          Create one for free
        </Link>
      </p>
    </div>
  );
}
