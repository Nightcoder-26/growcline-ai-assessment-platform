"use client";

/**
 * /resume-onboarding — Resume Upload & AI Skill Extraction Page
 * Candidate onboarding step after login/signup.
 */

import { useState, useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import {
  Upload,
  FileText,
  CheckCircle2,
  AlertCircle,
  Sparkles,
  ArrowRight,
  RefreshCw,
  X,
  FileCheck,
  BrainCircuit,
  Zap,
  Code2,
  ShieldCheck,
} from "lucide-react";
import AppShell from "@/components/assessment/AppShell";
import { getStoredToken } from "@/services/authService";
import {
  uploadResume,
  getResumeStatus,
  deleteResume,
  type SkillProfile,
} from "@/services/resumeService";

export default function ResumeOnboardingPage() {
  const router = useRouter();
  const fileInputRef = useRef<HTMLInputElement>(null);

  const [checkingStatus, setCheckingStatus] = useState(true);
  const [hasExistingResume, setHasExistingResume] = useState(false);
  const [existingFilename, setExistingFilename] = useState<string | null>(null);

  const [file, setFile] = useState<File | null>(null);
  const [dragActive, setDragActive] = useState(false);

  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [statusText, setStatusText] = useState("");

  const [profile, setProfile] = useState<SkillProfile | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Check auth and existing resume status
  useEffect(() => {
    const token = getStoredToken();
    if (!token) {
      router.replace("/login");
      return;
    }

    getResumeStatus()
      .then((status) => {
        if (status.hasResume) {
          setHasExistingResume(true);
          setExistingFilename(status.resumeFilename);
        }
      })
      .catch(() => {})
      .finally(() => setCheckingStatus(false));
  }, [router]);

  // Drag and drop handlers
  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      validateAndSetFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      validateAndSetFile(e.target.files[0]);
    }
  };

  const validateAndSetFile = (f: File) => {
    setError(null);
    const ext = f.name.includes(".") ? f.name.split(".").pop()?.toLowerCase() : "";
    if (ext !== "pdf" && ext !== "docx" && ext !== "doc") {
      setError("Please upload a PDF or DOCX file.");
      return;
    }
    if (f.size > 15 * 1024 * 1024) {
      setError("File size exceeds 15MB limit.");
      return;
    }
    setFile(f);
  };

  const handleUploadAndAnalyze = async () => {
    if (!file) return;

    setUploading(true);
    setError(null);
    setProgress(20);
    setStatusText("Uploading resume...");

    try {
      setTimeout(() => {
        setProgress(50);
        setStatusText("Extracting resume text...");
      }, 800);

      setTimeout(() => {
        setProgress(75);
        setStatusText("Groq AI analyzing skills & experience...");
      }, 1800);

      const extractedProfile = await uploadResume(file);
      setProgress(100);
      setStatusText("Analysis complete!");
      setProfile(extractedProfile);
      setHasExistingResume(true);
      setExistingFilename(file.name);
    } catch (err: any) {
      setError(err?.response?.data?.message || err?.message || "Failed to analyze resume. Please try again.");
    } finally {
      setUploading(false);
    }
  };

  const handleReupload = async () => {
    try {
      await deleteResume();
      setHasExistingResume(false);
      setExistingFilename(null);
      setProfile(null);
      setFile(null);
    } catch (err: any) {
      setError(err?.message || "Failed to reset resume.");
    }
  };

  return (
    <AppShell title="Resume Onboarding" subtitle="Personalize your assessment experience">
      <div className="max-w-3xl mx-auto space-y-7 pb-10">

        {/* ── Banner ────────────────────────────────────────────────── */}
        <div className="rounded-2xl p-6 bg-[#1E293B] border border-white/10 text-white relative overflow-hidden shadow-sm">
          <div
            className="absolute top-0 right-0 w-72 h-72 rounded-full opacity-10 blur-3xl pointer-events-none"
            style={{ background: "#4096ff" }}
          />
          <div className="relative flex items-start gap-4">
            <div className="w-12 h-12 rounded-xl bg-[#4096ff]/20 border border-[#4096ff]/30 flex items-center justify-center shrink-0">
              <Sparkles size={24} className="text-[#60a5fa]" />
            </div>
            <div>
              <div className="flex items-center gap-2 mb-1">
                <span className="px-2.5 py-0.5 rounded-full text-[10px] font-extrabold uppercase tracking-wide bg-[#4096ff]/20 text-[#60a5fa] border border-[#4096ff]/30">
                  AI Personalization
                </span>
              </div>
              <h2 className="text-[20px] font-extrabold text-white leading-snug">
                Upload Your Resume to Personalize Your Assessments
              </h2>
              <p className="text-[13px] text-[#94A3B8] mt-1 leading-relaxed">
                Our Groq AI engine analyzes your experience, technical skills, and projects to generate 
                custom <strong className="text-white">25 Aptitude</strong>, <strong className="text-white">25 Technical</strong>, and <strong className="text-white">15 Coding</strong> problems tailored specifically to you.
              </p>
            </div>
          </div>
        </div>

        {/* ── Step Tracker ───────────────────────────────────────────── */}
        {!checkingStatus && (
          <div className="grid grid-cols-4 gap-3 bg-white border border-[rgba(30,41,59,0.08)] rounded-xl p-4 shadow-sm">
            {[
              { step: 1, label: "Account", active: false, done: true },
              { step: 2, label: "Resume", active: !profile && !hasExistingResume && !uploading, done: !!profile || hasExistingResume || !!file },
              { step: 3, label: "Analysis", active: uploading, done: !!profile },
              { step: 4, label: "Ready", active: !!profile, done: !!profile },
            ].map((s) => (
              <div key={s.step} className="flex flex-col gap-1.5">
                <div className={`h-1.5 rounded-full transition-all duration-300 ${
                  s.done ? "bg-[#4096ff]" : s.active ? "bg-[#4096ff]/50 animate-pulse" : "bg-slate-200"
                }`} />
                <span className={`text-[10.5px] font-bold tracking-tight ${
                  s.done || s.active ? "text-[#1E293B]" : "text-slate-400"
                }`}>
                  Step {s.step} — {s.label}
                </span>
              </div>
            ))}
          </div>
        )}

        {/* ── Main Content Area ─────────────────────────────────────── */}
        {checkingStatus ? (
          <div className="bg-white border border-[rgba(30,41,59,0.10)] rounded-2xl p-12 text-center">
            <div className="w-8 h-8 border-3 border-[#4096ff] border-t-transparent rounded-full animate-spin mx-auto mb-3" />
            <p className="text-[13px] text-[#64748B]">Checking your resume status...</p>
          </div>
        ) : profile ? (
          /* ── Extraction Result Success State ─────────────────────── */
          <div className="bg-white border border-[rgba(30,41,59,0.10)] rounded-2xl p-7 space-y-6 animate-fade-in-up">
            <div className="flex items-center justify-between pb-4 border-b border-[rgba(30,41,59,0.07)]">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-[#4096ff]/10 text-[#4096ff] flex items-center justify-center">
                  <FileCheck size={22} />
                </div>
                <div>
                  <h3 className="text-[15px] font-bold text-[#1E293B]">Resume Analysis Complete</h3>
                  <p className="text-[12px] text-[#64748B]">{existingFilename || "Resume uploaded successfully"}</p>
                </div>
              </div>
              <span className="px-3 py-1 rounded-full text-[11px] font-bold bg-[#4096ff]/10 text-[#4096ff] border border-[#4096ff]/20 flex items-center gap-1">
                <CheckCircle2 size={12} /> Verified Profile
              </span>
            </div>

            {/* Profile Overview Grid */}
            <div className="grid sm:grid-cols-2 gap-4">
              <div className="bg-[#F8FAFC] border border-[rgba(30,41,59,0.08)] rounded-xl p-4">
                <p className="text-[11px] font-bold text-[#64748B] uppercase tracking-wide mb-1">Experience Level</p>
                <p className="text-[16px] font-extrabold text-[#1E293B]">
                  {profile.experience_level || "Junior"}
                </p>
              </div>

              <div className="bg-[#F8FAFC] border border-[rgba(30,41,59,0.08)] rounded-xl p-4">
                <p className="text-[11px] font-bold text-[#64748B] uppercase tracking-wide mb-1">Extracted Technologies</p>
                <p className="text-[16px] font-extrabold text-[#4096ff]">
                  {(profile.programming_languages?.length || 0) + (profile.frameworks?.length || 0) + (profile.databases?.length || 0)} Technologies Found
                </p>
              </div>
            </div>

            {/* Extracted Skills Chips */}
            {profile.programming_languages && profile.programming_languages.length > 0 && (
              <div>
                <p className="text-[12px] font-bold text-[#1E293B] mb-2 flex items-center gap-1.5">
                  <Code2 size={14} className="text-[#4096ff]" /> Programming Languages
                </p>
                <div className="flex flex-wrap gap-2">
                  {profile.programming_languages.map((lang) => (
                    <span
                      key={lang}
                      className="px-3 py-1 rounded-lg text-[12px] font-semibold bg-[#4096ff]/10 text-[#4096ff] border border-[#4096ff]/20"
                    >
                      {lang}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {profile.frameworks && profile.frameworks.length > 0 && (
              <div>
                <p className="text-[12px] font-bold text-[#1E293B] mb-2 flex items-center gap-1.5">
                  <Zap size={14} className="text-[#4096ff]" /> Frameworks & Libraries
                </p>
                <div className="flex flex-wrap gap-2">
                  {profile.frameworks.concat(profile.libraries || []).map((fw) => (
                    <span
                      key={fw}
                      className="px-3 py-1 rounded-lg text-[12px] font-semibold bg-[#1E293B]/10 text-[#1E293B] border border-[#1E293B]/20"
                    >
                      {fw}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {profile.databases && profile.databases.length > 0 && (
              <div>
                <p className="text-[12px] font-bold text-[#1E293B] mb-2">Databases & Cloud</p>
                <div className="flex flex-wrap gap-2">
                  {profile.databases.concat(profile.cloud_technologies || []).map((db) => (
                    <span
                      key={db}
                      className="px-3 py-1 rounded-lg text-[12px] font-semibold bg-[#F1F5F9] text-[#64748B] border border-[rgba(30,41,59,0.1)]"
                    >
                      {db}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {profile.tools && profile.tools.length > 0 && (
              <div>
                <p className="text-[12px] font-bold text-[#1E293B] mb-2">Developer Tools</p>
                <div className="flex flex-wrap gap-2">
                  {profile.tools.map((t) => (
                    <span
                      key={t}
                      className="px-3 py-1 rounded-lg text-[12px] font-semibold bg-[#F8FAFC] text-[#475569] border border-slate-200"
                    >
                      {t}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {profile.domains && profile.domains.length > 0 && (
              <div>
                <p className="text-[12px] font-bold text-[#1E293B] mb-2">Specialized Domains</p>
                <div className="flex flex-wrap gap-2">
                  {profile.domains.map((d) => (
                    <span
                      key={d}
                      className="px-3 py-1 rounded-lg text-[12px] font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200"
                    >
                      {d}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {profile.projects && profile.projects.length > 0 && (
              <div>
                <p className="text-[12px] font-bold text-[#1E293B] mb-2">Notable Projects</p>
                <div className="space-y-2">
                  {profile.projects.map((proj, pIdx) => (
                    <div key={pIdx} className="p-3 rounded-lg bg-slate-50 border border-slate-200/60">
                      <p className="text-[13px] font-bold text-[#1E293B]">{proj.name}</p>
                      {proj.technologies && proj.technologies.length > 0 && (
                        <div className="flex flex-wrap gap-1.5 mt-1.5">
                          {proj.technologies.map((t) => (
                            <span key={t} className="px-2 py-0.5 rounded bg-white text-[11px] text-[#64748B] border border-slate-200">
                              {t}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Action Buttons */}
            <div className="flex flex-col sm:flex-row items-center justify-between gap-3 pt-4 border-t border-[rgba(30,41,59,0.07)]">
              <button
                onClick={handleReupload}
                className="text-[12.5px] text-[#64748B] hover:text-[#1E293B] font-semibold flex items-center gap-1.5 transition-colors"
              >
                <RefreshCw size={13} /> Upload Different Resume
              </button>

              <button
                onClick={() => router.push("/dashboard")}
                className="w-full sm:w-auto px-6 py-3 rounded-xl bg-[#4096ff] hover:bg-[#60a5fa] text-white text-[13.5px] font-bold transition-all shadow-md flex items-center justify-center gap-2"
              >
                Continue to Assessment Dashboard <ArrowRight size={15} />
              </button>
            </div>
          </div>
        ) : (
          /* ── Upload Area State ───────────────────────────────────── */
          <div className="bg-white border border-[rgba(30,41,59,0.10)] rounded-2xl p-7 space-y-6">

            {hasExistingResume && (
              <div className="p-4 rounded-xl bg-[#4096ff]/10 border border-[#4096ff]/20 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <FileCheck size={20} className="text-[#4096ff]" />
                  <div>
                    <p className="text-[13px] font-bold text-[#1E293B]">Resume Already Analyzed</p>
                    <p className="text-[12px] text-[#64748B]">{existingFilename || "Your resume is active"}</p>
                  </div>
                </div>
                <button
                  onClick={() => router.push("/dashboard")}
                  className="px-4 py-2 rounded-lg bg-[#4096ff] hover:bg-[#60a5fa] text-white text-[12px] font-bold transition-colors flex items-center gap-1"
                >
                  Go to Dashboard <ArrowRight size={13} />
                </button>
              </div>
            )}

            {/* Drag & Drop Zone */}
            <div
              onDragEnter={handleDrag}
              onDragLeave={handleDrag}
              onDragOver={handleDrag}
              onDrop={handleDrop}
              onClick={() => fileInputRef.current?.click()}
              className={`border-2 border-dashed rounded-2xl p-9 text-center cursor-pointer transition-all duration-200 ${
                dragActive
                  ? "border-[#4096ff] bg-[#4096ff]/5 scale-[0.99]"
                  : "border-[#CBD5E1] hover:border-[#4096ff] hover:bg-[#F8FAFC]"
              }`}
            >
              <input
                ref={fileInputRef}
                type="file"
                accept=".pdf,.docx,.doc"
                onChange={handleFileChange}
                className="hidden"
              />

              <div className="w-14 h-14 rounded-2xl bg-[#4096ff]/10 text-[#4096ff] flex items-center justify-center mx-auto mb-4">
                <Upload size={26} />
              </div>

              <h3 className="text-[15px] font-bold text-[#1E293B]">
                {file ? file.name : "Drag & drop your resume here"}
              </h3>
              <p className="text-[12.5px] text-[#64748B] mt-1">
                {file
                  ? `${(file.size / (1024 * 1024)).toFixed(2)} MB • Ready to analyze`
                  : "or click to browse from your computer"}
              </p>

              <div className="flex items-center justify-center gap-4 mt-4 text-[11.5px] text-[#94A3B8]">
                <span>Supported: PDF, DOCX</span>
                <span>•</span>
                <span>Max size: 15MB</span>
              </div>
            </div>

            {/* Error Display */}
            {error && (
              <div className="p-3.5 rounded-xl bg-red-50 border border-red-200 text-red-700 text-[12.5px] flex items-center gap-2">
                <AlertCircle size={16} className="shrink-0" />
                <span>{error}</span>
              </div>
            )}

            {/* Uploading Progress */}
            {uploading && (
              <div className="space-y-2 p-4 rounded-xl bg-[#F8FAFC] border border-[rgba(30,41,59,0.08)]">
                <div className="flex justify-between text-[12px] font-bold text-[#1E293B]">
                  <span>{statusText}</span>
                  <span>{progress}%</span>
                </div>
                <div className="w-full h-2 rounded-full bg-[#E2E8F0] overflow-hidden">
                  <div
                    className="h-full bg-[#4096ff] transition-all duration-300 rounded-full"
                    style={{ width: `${progress}%` }}
                  />
                </div>
              </div>
            )}

            {/* Analyze Action Button */}
            <div className="flex justify-end pt-2">
              <button
                disabled={!file || uploading}
                onClick={handleUploadAndAnalyze}
                className="w-full sm:w-auto px-7 py-3 rounded-xl bg-[#4096ff] hover:bg-[#60a5fa] disabled:bg-[#CBD5E1] disabled:cursor-not-allowed text-white text-[13.5px] font-bold transition-all shadow-md flex items-center justify-center gap-2"
              >
                {uploading ? (
                  <>
                    <RefreshCw size={15} className="animate-spin" /> Analyzing Resume...
                  </>
                ) : (
                  <>
                    Analyze Resume & Personalize <Sparkles size={15} />
                  </>
                )}
              </button>
            </div>
          </div>
        )}

        {/* ── Feature Guarantee Info Cards ──────────────────────────── */}
        <div className="grid sm:grid-cols-3 gap-4">
          <div className="bg-white border border-[rgba(30,41,59,0.10)] rounded-xl p-4 flex items-start gap-3">
            <div className="w-2 h-2 rounded-full bg-[#4096ff] mt-1.5 shrink-0" />
            <div>
              <p className="text-[12.5px] font-bold text-[#1E293B]">25 Aptitude MCQs</p>
              <p className="text-[11.5px] text-[#64748B]">Quantitative, logical, and analytical reasoning</p>
            </div>
          </div>

          <div className="bg-white border border-[rgba(30,41,59,0.10)] rounded-xl p-4 flex items-start gap-3">
            <div className="w-2 h-2 rounded-full bg-[#4096ff] mt-1.5 shrink-0" />
            <div>
              <p className="text-[12.5px] font-bold text-[#1E293B]">25 Technical MCQs</p>
              <p className="text-[11.5px] text-[#64748B]">Matched strictly to your programming stack</p>
            </div>
          </div>

          <div className="bg-white border border-[rgba(30,41,59,0.10)] rounded-xl p-4 flex items-start gap-3">
            <div className="w-2 h-2 rounded-full bg-[#4096ff] mt-1.5 shrink-0" />
            <div>
              <p className="text-[12.5px] font-bold text-[#1E293B]">15 Coding Problems</p>
              <p className="text-[11.5px] text-[#64748B]">LeetCode-style algorithmic challenges</p>
            </div>
          </div>
        </div>

      </div>
    </AppShell>
  );
}
