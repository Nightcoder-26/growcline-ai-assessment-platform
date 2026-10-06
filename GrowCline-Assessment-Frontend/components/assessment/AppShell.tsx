"use client";

/**
 * AppShell — Authenticated application wrapper
 * Provides top header + left sidebar navigation for all Team A pages.
 * Team B pages (/video-recording, /interview-analytics) run outside this shell.
 */

import { useState, useEffect } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import {
  LayoutDashboard,
  ClipboardList,
  Video,
  BarChart2,
  Trophy,
  Menu,
  X,
  LogOut,
  ChevronRight,
  Sparkles,
} from "lucide-react";
import { clearAuth, getStoredUser } from "@/services/authService";
import SidebarGuideCarousel from "@/components/assessment/SidebarGuideCarousel";
import UserProfileDrawer from "@/components/assessment/UserProfileDrawer";

interface NavItem {
  label: string;
  href: string;
  icon: React.ElementType;
  exact?: boolean;
}

const NAV_ITEMS: NavItem[] = [
  { label: "Home",        href: "/dashboard",       icon: LayoutDashboard, exact: true },
  { label: "Assessments", href: "/assessments",     icon: ClipboardList },
  { label: "Interview",   href: "/video-recording", icon: Video, exact: true },
  { label: "Results",     href: "/results",         icon: Trophy, exact: true },
  { label: "Analytics",   href: "/analytics",       icon: BarChart2, exact: true },
];

interface AppShellProps {
  children: React.ReactNode;
  title?: string;
  subtitle?: string;
}

export default function AppShell({ children, title, subtitle }: AppShellProps) {
  const pathname   = usePathname();
  const router     = useRouter();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [user, setUser] = useState<{ fullName: string; email: string; role: string } | null>(null);
  const [profileDrawerOpen, setProfileDrawerOpen] = useState(false);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    const stored = getStoredUser();
    if (stored) setUser(stored);
    setMounted(true);
  }, []);

  // Close sidebar on Escape key
  useEffect(() => {
    function handleKeyDown(e: KeyboardEvent) {
      if (e.key === "Escape" && sidebarOpen) setSidebarOpen(false);
    }
    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, [sidebarOpen]);

  function isActive(item: NavItem) {
    if (item.exact) return pathname === item.href;
    return pathname.startsWith(item.href);
  }

  function handleLogout() {
    clearAuth();
    router.push("/login");
  }

  const initials = user?.fullName
    ? user.fullName.split(" ").map((w) => w[0]).slice(0, 2).join("").toUpperCase()
    : "U";

  return (
    <div className="min-h-screen bg-[#F8FAFC] flex">
      {/* User Profile Slide-Over Drawer */}
      <UserProfileDrawer
        isOpen={profileDrawerOpen}
        onClose={() => setProfileDrawerOpen(false)}
      />

      {/* ── Sidebar ─────────────────────────────────────────────── */}
      {/* Mobile overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-[#0F172A]/50 z-30 lg:hidden backdrop-blur-sm"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      <aside
        className={`
          fixed top-0 left-0 h-screen w-64 z-40 flex flex-col
          transform transition-transform duration-300 ease-in-out
          ${sidebarOpen ? "translate-x-0" : "-translate-x-full"}
          lg:translate-x-0 lg:sticky lg:top-0 lg:h-screen lg:shrink-0 lg:z-30
        `}
        style={{
          background: "linear-gradient(180deg, #0F172A 0%, #1E293B 100%)",
          borderRight: "1px solid rgba(255,255,255,0.06)",
        }}
      >
        {/* Logo */}
        <div className="flex items-center justify-between h-16 px-5 shrink-0"
          style={{ borderBottom: "1px solid rgba(255,255,255,0.06)" }}
        >
          <Link href="/dashboard" className="flex items-center gap-2.5 group">
            {/* Gradient G mark */}
            <div
              className="w-8 h-8 rounded-xl flex items-center justify-center shadow-[0_4px_12px_rgba(64,150,255,0.4)] transition-transform duration-200 group-hover:scale-105"
              style={{ background: "linear-gradient(135deg, #4096ff 0%, #818cf8 100%)" }}
            >
              <Sparkles size={14} className="text-white" />
            </div>
            <div>
              <span className="text-white font-bold text-[15px] tracking-[-0.02em]">
                Grow<span style={{ color: "#60a5fa" }}>Cline</span>
              </span>
            </div>
          </Link>
          <button
            className="lg:hidden text-white/50 hover:text-white transition-colors p-1 rounded-lg hover:bg-white/10"
            onClick={() => setSidebarOpen(false)}
            aria-label="Close navigation menu"
          >
            <X size={17} />
          </button>
        </div>

        {/* Navigation label */}
        <div className="px-5 pt-4 pb-1 shrink-0">
          <span className="text-[10px] font-bold text-white/25 uppercase tracking-[0.12em]">
            Navigation
          </span>
        </div>

        {/* Navigation */}
        <nav className="py-1 px-3 space-y-0.5 shrink-0">
          {NAV_ITEMS.map((item) => {
            const active = isActive(item);
            const Icon   = item.icon;
            return (
              <Link
                key={item.href}
                href={item.href}
                onClick={() => setSidebarOpen(false)}
                aria-label={item.label}
                aria-current={active ? "page" : undefined}
                className={`
                  flex items-center gap-3 px-3 py-2.5 rounded-xl text-[13px] font-medium
                  transition-all duration-150 group relative
                  ${active
                    ? "text-white"
                    : "text-[#64748B] hover:text-[#94A3B8] hover:bg-white/5"
                  }
                `}
                style={active ? {
                  background: "linear-gradient(135deg, rgba(64,150,255,0.25) 0%, rgba(64,150,255,0.08) 100%)",
                  borderLeft: "2px solid #4096ff",
                  boxShadow: "0 2px 8px rgba(64,150,255,0.15)",
                } : { borderLeft: "2px solid transparent" }}
              >
                <Icon
                  size={15}
                  className={`shrink-0 transition-colors ${active ? "text-[#4096ff]" : "text-[#475569] group-hover:text-[#64748B]"}`}
                />
                <span className="flex-1">{item.label}</span>
                {active && (
                  <ChevronRight size={12} className="shrink-0 text-[#4096ff]/60" />
                )}
              </Link>
            );
          })}
        </nav>

        {/* Platform Info & Rules Carousel Widget */}
        <SidebarGuideCarousel />

        {/* User profile footer */}
        <div className="p-3 shrink-0 mt-auto" style={{ borderTop: "1px solid rgba(255,255,255,0.06)" }}>
          <div className="flex items-center gap-3 px-2 py-2 group">
            <button
              onClick={() => setProfileDrawerOpen(true)}
              className="flex items-center gap-3 flex-1 min-w-0 text-left hover:opacity-90 transition-opacity"
              title="Open Profile"
            >
              {/* Avatar with gradient ring */}
              <div className="relative shrink-0">
                <div
                  className="w-8 h-8 rounded-full flex items-center justify-center transition-all duration-200 group-hover:ring-2 group-hover:ring-[#4096ff]/50"
                  style={{ background: "linear-gradient(135deg, rgba(64,150,255,0.3), rgba(129,140,248,0.3))", border: "1px solid rgba(64,150,255,0.35)" }}
                >
                  <span className="text-[#93C5FD] text-xs font-bold">{initials}</span>
                </div>
                {/* Online indicator */}
                <span className="absolute -bottom-0.5 -right-0.5 w-2.5 h-2.5 rounded-full bg-[#10b981] border-2 border-[#0F172A]" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-white text-[12.5px] font-semibold truncate group-hover:text-[#93C5FD] transition-colors">
                  {user?.fullName ?? "Candidate"}
                </p>
                <p className="text-[#475569] text-[11px] truncate capitalize">
                  {user?.role ?? "candidate"}
                </p>
              </div>
            </button>
            <button
              onClick={handleLogout}
              title="Sign out"
              className="text-[#475569] hover:text-white transition-colors shrink-0 p-1.5 rounded-lg hover:bg-white/10"
            >
              <LogOut size={14} />
            </button>
          </div>
        </div>
      </aside>

      {/* ── Main content ─────────────────────────────────────────── */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Top header */}
        <header className="h-16 bg-white/95 backdrop-blur-md flex items-center px-5 gap-4 shrink-0 sticky top-0 z-20"
          style={{ borderBottom: "1px solid rgba(30,41,59,0.07)", boxShadow: "0 1px 0 rgba(30,41,59,0.04), 0 4px 16px rgba(30,41,59,0.03)" }}
        >
          {/* Mobile hamburger */}
          <button
            className="lg:hidden text-[#64748B] hover:text-[#1E293B] transition-colors p-1.5 rounded-lg hover:bg-[#F1F5F9]"
            onClick={() => setSidebarOpen(true)}
            aria-label="Open navigation menu"
          >
            <Menu size={19} />
          </button>

          {/* Page title */}
          <div className="flex-1 min-w-0">
            {title && (
              <h1 className="text-[15px] font-bold text-[#1E293B] truncate leading-tight">
                {title}
              </h1>
            )}
            {subtitle && (
              <p className="text-[11.5px] text-[#94A3B8] truncate">{subtitle}</p>
            )}
          </div>

          {/* Right: badge */}
          <div className="flex items-center gap-2 shrink-0">
            <button
              onClick={() => setProfileDrawerOpen(true)}
              className="hidden sm:flex items-center gap-2 pl-3 ml-1 hover:opacity-80 transition-opacity"
              style={{ borderLeft: "1px solid rgba(30,41,59,0.08)" }}
              title="Open Profile"
            >
              <div
                className="w-7 h-7 rounded-full flex items-center justify-center"
                style={{ background: "linear-gradient(135deg, rgba(64,150,255,0.15), rgba(129,140,248,0.15))", border: "1px solid rgba(64,150,255,0.25)" }}
              >
                <span className="text-[#4096ff] text-[11px] font-bold">{initials}</span>
              </div>
              <span className="text-[13px] font-semibold text-[#1E293B] max-w-[120px] truncate">
                {user?.fullName ?? "Candidate"}
              </span>
            </button>
          </div>
        </header>

        {/* Page content */}
        <main className={`flex-1 p-5 lg:p-7 overflow-auto ${mounted ? "animate-fade-in-up" : ""}`}>
          {children}
        </main>
      </div>
    </div>
  );
}
