"use client";

/**
 * SignupForm — Full registration form with validation, role selection,
 * terms checkbox, and backend integration.
 */

import { useState, useId } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import {
  Eye, EyeOff, Mail, Lock, User, ArrowRight,
  Loader2, AlertCircle, CheckCircle2,
} from "lucide-react";
import { register } from "@/services/authService";

// ─── Types ─────────────────────────────────────────────────────────────────────
type Role = "candidate" | "recruiter" | "admin";

interface FormErrors {
  fullName?: string;
  email?: string;
  password?: string;
  confirmPassword?: string;
  role?: string;
  terms?: string;
  general?: string;
}

// ─── Password strength meter ───────────────────────────────────────────────────
function getPasswordStrength(p: string): { score: number; label: string; color: string } {
  if (!p) return { score: 0, label: "", color: "" };
  let score = 0;
  if (p.length >= 8) score++;
  if (/[A-Z]/.test(p)) score++;
  if (/[0-9]/.test(p)) score++;
  if (/[^A-Za-z0-9]/.test(p)) score++;

  if (score <= 1) return { score, label: "Weak", color: "#EF4444" };
  if (score === 2) return { score, label: "Fair", color: "#F59E0B" };
  if (score === 3) return { score, label: "Good", color: "#3B82F6" };
  return { score, label: "Strong", color: "#10B981" };
}

// ─── Validate ──────────────────────────────────────────────────────────────────
function validateForm(
  fullName: string,
  email: string,
  password: string,
  confirmPassword: string,
  role: Role | "",
  terms: boolean
): FormErrors {
  const errors: FormErrors = {};

  if (!fullName.trim()) errors.fullName = "Full name is required.";
  else if (fullName.trim().length < 2) errors.fullName = "Name must be at least 2 characters.";

  if (!email.trim()) errors.email = "Email is required.";
  else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) errors.email = "Invalid email address.";

  if (!password) errors.password = "Password is required.";
  else if (password.length < 8) errors.password = "Password must be at least 8 characters.";

  if (!confirmPassword) errors.confirmPassword = "Please confirm your password.";
  else if (password !== confirmPassword) errors.confirmPassword = "Passwords do not match.";

  if (!role) errors.role = "Please select your role.";

  if (!terms) errors.terms = "You must accept the Terms & Privacy Policy.";

  return errors;
}

// ─── Field wrapper ─────────────────────────────────────────────────────────────
function Field({
  id, label, error, children,
}: {
  id: string; label: string; error?: string; children: React.ReactNode;
}) {
  return (
    <div className="space-y-1.5">
      <label htmlFor={id} className="block text-[13px] font-semibold text-[#1E293B]">
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

// ─── Input ─────────────────────────────────────────────────────────────────────
function Input({
  id, type, placeholder, value, onChange, hasError,
  icon: Icon, rightSlot, autoComplete,
}: {
  id: string; type: string; placeholder: string; value: string;
  onChange: (v: string) => void; hasError?: boolean;
  icon: React.ElementType; rightSlot?: React.ReactNode; autoComplete?: string;
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
        className={`w-full h-[46px] pl-10 bg-white border rounded-[11px] text-[14px] text-[#1E293B] placeholder-[#CBD5E1] outline-none transition-all
          ${hasError
            ? "border-[#EF4444] focus:border-[#EF4444] focus:ring-2 focus:ring-[#EF4444]/20"
            : "border-[rgba(30,41,59,0.14)] focus:border-[#4096FF] focus:ring-2 focus:ring-[#4096FF]/15"
          }`}
        style={{ paddingRight: rightSlot ? "3rem" : "1rem" }}
      />
      {rightSlot && (
        <div className="absolute right-3.5 top-1/2 -translate-y-1/2">{rightSlot}</div>
      )}
    </div>
  );
}

// ─── Role pill ─────────────────────────────────────────────────────────────────
const ROLES: { value: Role; label: string; desc: string }[] = [
  { value: "candidate", label: "Candidate", desc: "Take assessments & interviews" },
  { value: "recruiter", label: "Recruiter",  desc: "Manage hiring pipelines" },
  { value: "admin",     label: "Admin",      desc: "Full platform access" },
];

function RolePill({
  role, selected, onSelect,
}: {
  role: (typeof ROLES)[number]; selected: boolean; onSelect: () => void;
}) {
  return (
    <button
      type="button"
      onClick={onSelect}
      className={`flex-1 min-w-[90px] flex flex-col items-center gap-1 py-3 px-2 rounded-[11px] border text-center transition-all ${
        selected
          ? "border-[#4096FF] bg-[#EFF6FF] ring-2 ring-[#4096FF]/20"
          : "border-[rgba(30,41,59,0.14)] bg-white hover:border-[#4096FF]/40 hover:bg-[#F8FAFC]"
      }`}
    >
      {selected && (
        <CheckCircle2 size={14} className="text-[#4096FF] mb-0.5" />
      )}
      <span className={`text-[13px] font-semibold ${selected ? "text-[#4096FF]" : "text-[#1E293B]"}`}>
        {role.label}
      </span>
      <span className="text-[10.5px] text-[#94A3B8] leading-tight">{role.desc}</span>
    </button>
  );
}

// ─── SignupForm ────────────────────────────────────────────────────────────────
export default function SignupForm() {
  const router  = useRouter();
  const uid     = useId();

  const [fullName, setFullName]             = useState("");
  const [email, setEmail]                   = useState("");
  const [password, setPassword]             = useState("");
  const [confirmPassword, setConfirmPass]   = useState("");
  const [showPass, setShowPass]             = useState(false);
  const [showConfirm, setShowConfirm]       = useState(false);
  const [role, setRole]                     = useState<Role | "">("");
  const [terms, setTerms]                   = useState(false);
  const [errors, setErrors]                 = useState<FormErrors>({});
  const [loading, setLoading]               = useState(false);
  const [successMsg, setSuccessMsg]         = useState("");

  const strength = getPasswordStrength(password);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setSuccessMsg("");

    const errs = validateForm(fullName, email, password, confirmPassword, role, terms);
    setErrors(errs);
    if (Object.keys(errs).length > 0) return;

    setLoading(true);
    try {
      await register({
        fullName: fullName.trim(),
        email: email.trim(),
        password,
        role: role as Role,
      });
      setSuccessMsg("Account created! Redirecting to login…");
      setTimeout(() => router.push("/login"), 1200);
    } catch (err: unknown) {
      const message =
        err instanceof Error ? err.message : "Registration failed. Please try again.";
      setErrors({ general: message });
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-5">
      {/* Header */}
      <div>
        <h1 className="text-[26px] font-extrabold text-[#1E293B] tracking-[-0.03em] leading-tight">
          Create your account 🚀
        </h1>
        <p className="mt-1.5 text-[14px] text-[#64748B]">
          Join thousands of teams already using AssessAI.
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
          <CheckCircle2 size={15} />
          {successMsg}
        </div>
      )}

      <form onSubmit={handleSubmit} noValidate className="space-y-4">
        {/* Full Name */}
        <Field id={`${uid}-name`} label="Full Name" error={errors.fullName}>
          <Input
            id={`${uid}-name`}
            type="text"
            placeholder="Jane Doe"
            value={fullName}
            onChange={setFullName}
            hasError={!!errors.fullName}
            icon={User}
            autoComplete="name"
          />
        </Field>

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
            placeholder="Min. 8 characters"
            value={password}
            onChange={setPassword}
            hasError={!!errors.password}
            icon={Lock}
            autoComplete="new-password"
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
          {/* Strength meter */}
          {password && (
            <div className="pt-1 space-y-1">
              <div className="flex gap-1">
                {[1, 2, 3, 4].map((i) => (
                  <div
                    key={i}
                    className="h-1 flex-1 rounded-full transition-all duration-300"
                    style={{
                      backgroundColor:
                        i <= strength.score ? strength.color : "rgba(30,41,59,0.08)",
                    }}
                  />
                ))}
              </div>
              <p className="text-[11px] font-medium" style={{ color: strength.color }}>
                {strength.label} password
              </p>
            </div>
          )}
        </Field>

        {/* Confirm Password */}
        <Field id={`${uid}-confirm`} label="Confirm Password" error={errors.confirmPassword}>
          <Input
            id={`${uid}-confirm`}
            type={showConfirm ? "text" : "password"}
            placeholder="Re-enter password"
            value={confirmPassword}
            onChange={setConfirmPass}
            hasError={!!errors.confirmPassword}
            icon={Lock}
            autoComplete="new-password"
            rightSlot={
              <button
                type="button"
                onClick={() => setShowConfirm((p) => !p)}
                className="text-[#94A3B8] hover:text-[#64748B] transition-colors"
                aria-label={showConfirm ? "Hide password" : "Show password"}
              >
                {showConfirm ? <EyeOff size={16} /> : <Eye size={16} />}
              </button>
            }
          />
        </Field>

        {/* Role selection */}
        <div className="space-y-2">
          <p className="text-[13px] font-semibold text-[#1E293B]">I am a…</p>
          <div className="flex gap-2 flex-wrap">
            {ROLES.map((r) => (
              <RolePill
                key={r.value}
                role={r}
                selected={role === r.value}
                onSelect={() => setRole(r.value)}
              />
            ))}
          </div>
          {errors.role && (
            <p className="flex items-center gap-1.5 text-[12px] text-[#EF4444] font-medium">
              <AlertCircle size={12} />
              {errors.role}
            </p>
          )}
        </div>

        {/* Terms checkbox */}
        <div className="space-y-1">
          <label className="flex items-start gap-2.5 cursor-pointer select-none">
            <input
              id={`${uid}-terms`}
              type="checkbox"
              checked={terms}
              onChange={(e) => setTerms(e.target.checked)}
              className="mt-0.5 w-4 h-4 rounded border-[rgba(30,41,59,0.25)] accent-[#4096FF] shrink-0"
            />
            <span className="text-[13px] text-[#64748B] leading-[1.6]">
              I agree to the{" "}
              <Link href="/terms" className="text-[#4096FF] hover:text-[#3580eb] font-medium transition-colors">
                Terms of Service
              </Link>{" "}
              and{" "}
              <Link href="/privacy" className="text-[#4096FF] hover:text-[#3580eb] font-medium transition-colors">
                Privacy Policy
              </Link>
              .
            </span>
          </label>
          {errors.terms && (
            <p className="flex items-center gap-1.5 text-[12px] text-[#EF4444] font-medium">
              <AlertCircle size={12} />
              {errors.terms}
            </p>
          )}
        </div>

        {/* Submit */}
        <button
          type="submit"
          disabled={loading}
          id="signup-submit-btn"
          className="w-full h-[48px] flex items-center justify-center gap-2 rounded-[11px] bg-[#4096FF] hover:bg-[#3580eb] disabled:opacity-70 disabled:cursor-not-allowed text-white text-[14.5px] font-semibold transition-all shadow-[0_4px_18px_rgba(64,150,255,0.42)] hover:shadow-[0_6px_28px_rgba(64,150,255,0.54)] hover:-translate-y-px active:translate-y-0"
        >
          {loading ? (
            <Loader2 size={18} className="animate-spin" />
          ) : (
            <>
              Create Account <ArrowRight size={15} />
            </>
          )}
        </button>
      </form>

      {/* Login link */}
      <p className="text-center text-[13.5px] text-[#64748B]">
        Already have an account?{" "}
        <Link
          href="/login"
          className="text-[#4096FF] hover:text-[#3580eb] font-semibold transition-colors"
        >
          Sign in
        </Link>
      </p>
    </div>
  );
}
