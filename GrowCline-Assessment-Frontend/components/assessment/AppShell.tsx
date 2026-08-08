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
} from "lucide-react";
import { clearAuth, getStoredUser } from "@/services/authService";
import SidebarGuideCarousel from "@/components/assessment/SidebarGuideCarousel";

interface NavItem {
  label: string;
  href: string;
  icon: React.ElementType;
  exact?: boolean;
}

const NAV_ITEMS: NavItem[] = [
  { label: "Home",        href: "/dashboard",   icon: LayoutDashboard, exact: true },
  { label: "Assessments", href: "/assessments", icon: ClipboardList },
  { label: "Interview",   href: "/video-recording", icon: Video, exact: true },
  { label: "Results",     href: "/results",     icon: Trophy, exact: true },
  { label: "Analytics",   href: "/analytics",   icon: BarChart2, exact: true },
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

  useEffect(() => {
    const stored = getStoredUser();
    if (stored) setUser(stored);
  }, []);

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
      {/* ── Sidebar ─────────────────────────────────────────────── */}
      {/* Mobile overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-[#0F172A]/40 z-30 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      <aside
        className={`
          fixed top-0 left-0 h-full w-60 bg-[#1E293B] z-40 flex flex-col
          transform transition-transform duration-200 ease-in-out
          ${sidebarOpen ? "translate-x-0" : "-translate-x-full"}
          lg:translate-x-0 lg:static lg:z-auto
        `}
      >
        {/* Logo */}
        <div className="flex items-center justify-between h-16 px-5 border-b border-white/10 shrink-0">
          <Link href="/dashboard" className="flex items-center gap-2.5">
            <div className="w-7 h-7 rounded-lg bg-[#4096ff] flex items-center justify-center">
              <span className="text-white text-xs font-bold">A</span>
            </div>
            <span className="text-white font-semibold text-[15px] tracking-[-0.01em]">
              AssessAI
            </span>
          </Link>
          <button
            className="lg:hidden text-white/60 hover:text-white transition-colors"
            onClick={() => setSidebarOpen(false)}
          >
            <X size={18} />
          </button>
        </div>

        {/* Navigation */}
        <nav className="flex-1 py-4 px-3 space-y-0.5 overflow-y-auto">
          {NAV_ITEMS.map((item) => {
            const active = isActive(item);
            const Icon   = item.icon;
            return (
              <Link
                key={item.href}
                href={item.href}
                onClick={() => setSidebarOpen(false)}
                className={`
                  flex items-center gap-3 px-3 py-2.5 rounded-lg text-[13.5px] font-medium
                  transition-all duration-150 group
                  ${active
                    ? "bg-[#4096ff] text-white shadow-[0_2px_8px_rgba(64,150,255,0.35)]"
                    : "text-[#94A3B8] hover:bg-white/8 hover:text-white"
                  }
                `}
              >
                <Icon size={16} className="shrink-0" />
                <span className="flex-1">{item.label}</span>
                {active && <ChevronRight size={13} className="shrink-0 opacity-60" />}
              </Link>
            );
          })}
        </nav>

        {/* Platform Info & Rules Carousel Widget */}
        <SidebarGuideCarousel />

        {/* User profile footer */}
        <div className="p-3 border-t border-white/10 shrink-0">
          <div className="flex items-center gap-3 px-2 py-2">
            <div className="w-8 h-8 rounded-full bg-[#4096ff]/20 border border-[#4096ff]/30 flex items-center justify-center shrink-0">
              <span className="text-[#4096ff] text-xs font-bold">{initials}</span>
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-white text-[12.5px] font-semibold truncate">
                {user?.fullName ?? "Candidate"}
              </p>
              <p className="text-[#64748B] text-[11px] truncate capitalize">
                {user?.role ?? "candidate"}
              </p>
            </div>
            <button
              onClick={handleLogout}
              title="Sign out"
              className="text-[#64748B] hover:text-white transition-colors shrink-0"
            >
              <LogOut size={15} />
            </button>
          </div>
        </div>
      </aside>

      {/* ── Main content ─────────────────────────────────────────── */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Top header */}
        <header className="h-16 bg-white border-b border-[rgba(30,41,59,0.08)] flex items-center px-5 gap-4 shrink-0 sticky top-0 z-20">
          {/* Mobile hamburger */}
          <button
            className="lg:hidden text-[#64748B] hover:text-[#1E293B] transition-colors"
            onClick={() => setSidebarOpen(true)}
          >
            <Menu size={20} />
          </button>

          {/* Page title */}
          <div className="flex-1 min-w-0">
            {title && (
              <h1 className="text-[15px] font-semibold text-[#1E293B] truncate leading-tight">
                {title}
              </h1>
            )}
            {subtitle && (
              <p className="text-[12px] text-[#64748B] truncate">{subtitle}</p>
            )}
          </div>

          {/* Right: user badge */}
          <div className="flex items-center gap-2 shrink-0">
            <div className="hidden sm:flex items-center gap-2 pl-3 border-l border-[rgba(30,41,59,0.08)]">
              <div className="w-7 h-7 rounded-full bg-[#4096ff]/10 border border-[#4096ff]/20 flex items-center justify-center">
                <span className="text-[#4096ff] text-[11px] font-bold">{initials}</span>
              </div>
              <span className="text-[13px] font-medium text-[#1E293B] max-w-[120px] truncate">
                {user?.fullName ?? "Candidate"}
              </span>
            </div>
          </div>
        </header>

        {/* Page content */}
        <main className="flex-1 p-5 lg:p-7 overflow-auto">
          {children}
        </main>
      </div>
    </div>
  );
}
