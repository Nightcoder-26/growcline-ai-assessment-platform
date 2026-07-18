"use client"

import { cn } from "@/lib/utils"

interface AudioWaveformProps {
  active: boolean
  bars?: number
  className?: string
}

// A lightweight, purely decorative equalizer used to signal live mic input.
export function AudioWaveform({ active, bars = 28, className }: AudioWaveformProps) {
  return (
    <div
      className={cn("flex h-8 items-center justify-center gap-[3px]", className)}
      aria-hidden="true"
    >
      {Array.from({ length: bars }).map((_, i) => {
        // Pseudo-random but stable heights and delays per bar.
        const seed = (i * 9301 + 49297) % 233280
        const base = 0.3 + (seed / 233280) * 0.7
        return (
          <span
            key={i}
            className={cn(
              "w-[3px] origin-center rounded-full bg-primary/70 transition-all duration-300",
              active ? "" : "!scale-y-[0.18] bg-muted-foreground/40",
            )}
            style={{
              height: `${Math.round(base * 100)}%`,
              animation: active
                ? `bar-bounce ${0.7 + base * 0.9}s ease-in-out ${i * 0.045}s infinite`
                : "none",
            }}
          />
        )
      })}
    </div>
  )
}
