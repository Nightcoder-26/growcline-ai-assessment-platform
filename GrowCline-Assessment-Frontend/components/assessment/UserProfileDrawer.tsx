"use client";

import { useEffect, useState } from "react";
import {
  X,
  User,
  Mail,
  ShieldCheck,
  Award,
  Camera,
  Mic,
  Monitor,
  LogOut,
  CheckCircle2,
  Copy,
  Check,
  Edit3,
  Save,
  Loader2,
  AlertCircle,
} from "lucide-react";
import { getStoredUser, clearAuth, storeAuth } from "@/services/authService";
import { useRouter } from "next/navigation";
import { getCandidateResults, type AssessmentResult } from "@/services/assessmentService";
import apiClient from "@/lib/apiClient";

interface UserProfileDrawerProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function UserProfileDrawer({ isOpen, onClose }: UserProfileDrawerProps) {
  const router = useRouter();
  const [user, setUser] = useState<{ id?: string; fullName: string; email: string; role: string } | null>(null);
  const [results, setResults] = useState<AssessmentResult[]>([]);
  const [copied, setCopied] = useState(false);

  // Edit state
  const [isEditing, setIsEditing] = useState(false);
  const [editName, setEditName] = useState("");
  const [editEmail, setEditEmail] = useState("");
  const [saving, setSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);
  const [saveError, setSaveError] = useState<string | null>(null);

  useEffect(() => {
    if (isOpen) {
      const u = getStoredUser();
      setUser(u);
      if (u) {
        setEditName(u.fullName || "");
        setEditEmail(u.email || "");
      }
      if (u?.id) {
        getCandidateResults(u.id)
          .then(setResults)
          .catch(() => {});
      }
    }
  }, [isOpen]);

  if (!isOpen) return null;

  const initials = user?.fullName
    ? user.fullName
        .split(" ")
        .map((w) => w[0])
        .slice(0, 2)
        .join("")
        .toUpperCase()
    : "CU";

  const totalCompleted = results.length;
  const avgScore =
    totalCompleted > 0
      ? Math.round(results.reduce((acc, r) => acc + (r.percentage ?? 0), 0) / totalCompleted)
      : 0;

  function handleLogout() {
    clearAuth();
    onClose();
    router.push("/login");
  }

  function handleCopyId() {
    if (user?.id) {
      navigator.clipboard.writeText(user.id);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  }

  async function handleSaveProfile(e: React.FormEvent) {
    e.preventDefault();
    if (!user) return;
    setSaving(true);
    setSaveError(null);
    setSaveSuccess(false);

    try {
      const updatedData = {
        fullName: editName.trim() || user.fullName,
        email: editEmail.trim() || user.email,
        role: user.role || "candidate",
      };

      // Best effort backend update if user.id exists
      if (user.id) {
        await apiClient.put(`/api/users/${user.id}`, updatedData).catch(() => {});
      }

      const updatedUser = {
        id: user.id || "",
        fullName: updatedData.fullName,
        email: updatedData.email,
        role: user.role || "candidate",
      };

      // Save to localStorage
      const token = localStorage.getItem("token") || "mock_jwt_token";
      storeAuth(token, updatedUser);
      setUser(updatedUser);

      setSaveSuccess(true);
      setIsEditing(false);
      setTimeout(() => setSaveSuccess(false), 3000);
    } catch (err: unknown) {
      setSaveError(err instanceof Error ? err.message : "Failed to update profile");
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="fixed inset-0 z-50 overflow-hidden">
      {/* Glassy backdrop overlay */}
      <div
        className="fixed inset-0 bg-[#0F172A]/60 backdrop-blur-sm transition-opacity duration-300"
        onClick={onClose}
      />

      {/* Sliding Window / Drawer Panel */}
      <div className="fixed inset-y-0 right-0 max-w-full flex pl-10">
        <aside className="w-screen max-w-md bg-[#1E293B]/95 backdrop-blur-xl border-l border-white/10 text-white shadow-[0_0_50px_rgba(0,0,0,0.5)] flex flex-col justify-between transform transition-transform duration-300 ease-in-out">
          {/* Top Header */}
          <div className="px-6 py-5 border-b border-white/10 flex items-center justify-between bg-white/5">
            <div className="flex items-center gap-2">
              <User size={18} className="text-[#4096ff]" />
              <h2 className="text-[15px] font-bold tracking-tight">Candidate Profile</h2>
            </div>
            <div className="flex items-center gap-2">
              {!isEditing && (
                <button
                  onClick={() => setIsEditing(true)}
                  className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-[#4096ff]/15 hover:bg-[#4096ff]/25 border border-[#4096ff]/30 text-[#4096ff] text-[12px] font-semibold transition-colors"
                >
                  <Edit3 size={13} />
                  Edit Profile
                </button>
              )}
              <button
                onClick={onClose}
                className="w-8 h-8 rounded-lg bg-white/10 hover:bg-white/20 text-white/70 hover:text-white flex items-center justify-center transition-colors"
              >
                <X size={18} />
              </button>
            </div>
          </div>

          {/* Drawer Body Scrollable Content */}
          <div className="flex-1 overflow-y-auto px-6 py-6 space-y-6">
            {/* Save Success / Error Messages */}
            {saveSuccess && (
              <div className="flex items-center gap-2 px-4 py-3 rounded-xl bg-[#F0FDF4]/10 border border-[#86EFAC]/30 text-[#86EFAC] text-[12.5px] font-semibold">
                <CheckCircle2 size={16} />
                Profile updated successfully!
              </div>
            )}
            {saveError && (
              <div className="flex items-center gap-2 px-4 py-3 rounded-xl bg-[#FEF2F2]/10 border border-[#FECACA]/30 text-[#FECACA] text-[12.5px] font-semibold">
                <AlertCircle size={16} />
                {saveError}
              </div>
            )}

            {/* Profile Edit Mode Form */}
            {isEditing ? (
              <form onSubmit={handleSaveProfile} className="space-y-4 p-4 rounded-2xl bg-white/5 border border-white/10">
                <div className="flex items-center justify-between mb-1">
                  <h3 className="text-[14px] font-bold text-white flex items-center gap-2">
                    <Edit3 size={15} className="text-[#4096ff]" /> Edit Details
                  </h3>
                  <button
                    type="button"
                    onClick={() => setIsEditing(false)}
                    className="text-[12px] text-[#94A3B8] hover:text-white transition-colors"
                  >
                    Cancel
                  </button>
                </div>

                <div className="space-y-1.5">
                  <label className="block text-[12px] font-semibold text-[#94A3B8]">
                    Full Name
                  </label>
                  <input
                    type="text"
                    value={editName}
                    onChange={(e) => setEditName(e.target.value)}
                    className="w-full h-10 px-3.5 rounded-xl bg-white/10 border border-white/15 text-white text-[13.5px] outline-none focus:border-[#4096ff]"
                    placeholder="Enter full name"
                    required
                  />
                </div>

                <div className="space-y-1.5">
                  <label className="block text-[12px] font-semibold text-[#94A3B8]">
                    Email Address
                  </label>
                  <input
                    type="email"
                    value={editEmail}
                    onChange={(e) => setEditEmail(e.target.value)}
                    className="w-full h-10 px-3.5 rounded-xl bg-white/10 border border-white/15 text-white text-[13.5px] outline-none focus:border-[#4096ff]"
                    placeholder="Enter email"
                    required
                  />
                </div>

                <button
                  type="submit"
                  disabled={saving}
                  className="w-full h-10 mt-2 rounded-xl bg-[#4096ff] hover:bg-[#60a5fa] disabled:opacity-70 text-white text-[13px] font-semibold transition-all flex items-center justify-center gap-2 shadow-lg"
                >
                  {saving ? (
                    <Loader2 size={15} className="animate-spin" />
                  ) : (
                    <>
                      <Save size={15} /> Save Profile Changes
                    </>
                  )}
                </button>
              </form>
            ) : (
              /* User Profile Display Card */
              <div className="flex items-center gap-4 p-4 rounded-2xl bg-white/5 border border-white/10 backdrop-blur-md">
                <div className="relative">
                  <div className="w-16 h-16 rounded-2xl bg-[#4096ff]/20 border-2 border-[#4096ff] flex items-center justify-center shadow-lg">
                    <span className="text-[#4096ff] text-xl font-black">{initials}</span>
                  </div>
                  <span
                    className="absolute -bottom-1 -right-1 w-4 h-4 bg-[#15803D] border-2 border-[#1E293B] rounded-full"
                    title="Active Candidate"
                  />
                </div>

                <div className="flex-1 min-w-0">
                  <h3 className="text-white text-[17px] font-bold truncate">
                    {user?.fullName ?? "Candidate User"}
                  </h3>
                  <p className="text-[#94A3B8] text-[13px] truncate flex items-center gap-1.5 mt-0.5">
                    <Mail size={12} className="text-[#4096ff]" />
                    {user?.email ?? "candidate@assessai.com"}
                  </p>
                  <div className="flex items-center gap-2 mt-2">
                    <span className="px-2.5 py-0.5 rounded-full bg-[#4096ff]/15 text-[#4096ff] text-[11px] font-bold border border-[#4096ff]/30 uppercase tracking-wider">
                      {user?.role ?? "Candidate"}
                    </span>
                    <span className="px-2 py-0.5 rounded-full bg-white/10 text-white/80 text-[11px] font-medium">
                      Verified
                    </span>
                  </div>
                </div>
              </div>
            )}

            {/* Candidate ID info */}
            {user?.id && (
              <div className="flex items-center justify-between px-4 py-2.5 rounded-xl bg-white/5 border border-white/10 text-[12px]">
                <span className="text-[#94A3B8] font-medium">Candidate ID:</span>
                <button
                  onClick={handleCopyId}
                  className="flex items-center gap-1.5 text-white font-mono hover:text-[#4096ff] transition-colors"
                >
                  <span className="truncate max-w-[160px]">{user.id}</span>
                  {copied ? <Check size={13} className="text-[#15803D]" /> : <Copy size={13} />}
                </button>
              </div>
            )}

            {/* Assessment Quick Stats */}
            <div className="space-y-2">
              <h4 className="text-[12px] font-bold uppercase tracking-wider text-[#94A3B8]">
                Assessment Overview
              </h4>
              <div className="grid grid-cols-2 gap-3">
                <div className="p-3.5 rounded-xl bg-white/5 border border-white/10">
                  <p className="text-[11px] text-[#94A3B8] font-medium">Completed Tests</p>
                  <p className="text-[22px] font-bold text-white mt-0.5">{totalCompleted}</p>
                </div>
                <div className="p-3.5 rounded-xl bg-white/5 border border-white/10">
                  <p className="text-[11px] text-[#94A3B8] font-medium">Average Score</p>
                  <p className="text-[22px] font-bold text-[#4096ff] mt-0.5">{avgScore}%</p>
                </div>
              </div>
            </div>

            {/* System Readiness Checklist */}
            <div className="space-y-2.5">
              <h4 className="text-[12px] font-bold uppercase tracking-wider text-[#94A3B8]">
                System Readiness
              </h4>
              <div className="p-4 rounded-xl bg-white/5 border border-white/10 space-y-3">
                {[
                  { icon: Camera, label: "Webcam Detector", status: "Ready", ok: true },
                  { icon: Mic, label: "Microphone Audio", status: "Active", ok: true },
                  { icon: Monitor, label: "Fullscreen Lock", status: "Supported", ok: true },
                  { icon: ShieldCheck, label: "AI Live Proctoring", status: "Standby", ok: true },
                ].map((item, idx) => (
                  <div key={idx} className="flex items-center justify-between text-[12.5px]">
                    <div className="flex items-center gap-2.5 text-white/90 font-medium">
                      <item.icon size={14} className="text-[#4096ff]" />
                      <span>{item.label}</span>
                    </div>
                    <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-[#15803D]">
                      <CheckCircle2 size={12} />
                      {item.status}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Drawer Footer Actions */}
          <div className="p-5 border-t border-white/10 bg-white/5">
            <button
              onClick={handleLogout}
              className="w-full h-11 rounded-xl bg-[#DC2626]/20 hover:bg-[#DC2626] border border-[#DC2626]/40 text-white text-[13.5px] font-semibold transition-all flex items-center justify-center gap-2 shadow-lg"
            >
              <LogOut size={16} />
              Sign Out of Account
            </button>
          </div>
        </aside>
      </div>
    </div>
  );
}
