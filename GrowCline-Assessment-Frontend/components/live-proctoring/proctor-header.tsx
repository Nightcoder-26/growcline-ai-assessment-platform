"use client";

import { ShieldCheck, Clock3, User, Briefcase } from "lucide-react";
import { useEffect, useState } from "react";

export function ProctorHeader() {
  const [clock, setClock] = useState("--:--");

  useEffect(() => {
    const updateClock = () => {
      setClock(
        new Date().toLocaleTimeString([], {
          hour: "2-digit",
          minute: "2-digit",
        })
      );
    };

    updateClock();

    const timer = setInterval(updateClock, 1000);

    return () => clearInterval(timer);
  }, []);

  return (
    <header className="rounded-2xl border border-white/10 bg-card p-6 shadow-xl">
      <div className="flex flex-col gap-6 lg:flex-row lg:items-center lg:justify-between">

        {/* Left Section */}
        <div className="space-y-3">

          <div className="flex items-center gap-3">
            <div className="rounded-xl bg-primary/15 p-3">
              <ShieldCheck className="h-7 w-7 text-primary" />
            </div>

            <div>
              <p className="text-sm text-muted-foreground">
                AI Interview Platform
              </p>

              <h1 className="text-3xl font-bold">
                Live Proctoring Dashboard
              </h1>
            </div>
          </div>

          <div className="flex flex-wrap gap-6 text-sm text-muted-foreground">

            <div className="flex items-center gap-2">
              <User size={16} />
              Candidate:
              <span className="font-medium text-foreground">
                John Smith
              </span>
            </div>

            <div className="flex items-center gap-2">
              <Briefcase size={16} />
              Role:
              <span className="font-medium text-foreground">
                Frontend Developer
              </span>
            </div>

          </div>
        </div>

        {/* Right Section */}

        <div className="flex items-center gap-6">

          <div className="flex items-center gap-2 rounded-xl bg-green-500/10 px-4 py-2">
            <span className="h-3 w-3 animate-pulse rounded-full bg-green-500"></span>

            <span className="font-semibold text-green-400">
              LIVE
            </span>
          </div>

          <div className="flex items-center gap-2 rounded-xl border border-white/10 bg-background px-4 py-2">

            <Clock3 size={18} />

            <span className="font-mono text-lg">
              {clock}
            </span>

          </div>

        </div>

      </div>
    </header>
  );
}