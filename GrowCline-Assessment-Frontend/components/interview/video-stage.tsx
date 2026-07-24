"use client";

import { useEffect, useRef, useState } from "react";
import Webcam from "react-webcam";
import {
  Maximize2,
  Mic,
  MicOff,
  Video,
  VideoOff,
  AlertTriangle,
  UserX,
} from "lucide-react";

interface VideoStageProps {
  webcamRef: React.RefObject<Webcam | null>;
  recording: boolean;
  paused: boolean;
  camOn: boolean;
  micOn: boolean;
  elapsed: string;
  take: number;
  faceDetected?: boolean;
  onToggleCam: () => void;
  onToggleMic: () => void;
  onFacePresenceChange?: (detected: boolean) => void;
  /** Fires when two or more distinct face regions are detected in frame. */
  onMultipleFacesDetected?: () => void;
}

export function VideoStage({
  webcamRef,
  recording,
  paused,
  camOn,
  micOn,
  elapsed,
  take,
  faceDetected = true,
  onToggleCam,
  onToggleMic,
  onFacePresenceChange,
  onMultipleFacesDetected,
}: VideoStageProps) {
  const live = recording && !paused;
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const [internalFaceDetected, setInternalFaceDetected] = useState(true);

  // Periodic Face / Subject Presence Check + Multiple-Face Detection via Canvas Pixel Analysis
  useEffect(() => {
    if (!camOn) {
      setInternalFaceDetected(false);
      onFacePresenceChange?.(false);
      return;
    }

    const interval = setInterval(() => {
      if (!webcamRef.current) return;
      const screenshot = webcamRef.current.getScreenshot();
      if (!screenshot) return;

      const img = new Image();
      img.onload = () => {
        if (!canvasRef.current) {
          canvasRef.current = document.createElement("canvas");
        }
        const canvas = canvasRef.current;
        const W = 160;
        const H = 90;
        canvas.width = W;
        canvas.height = H;
        const ctx = canvas.getContext("2d", { willReadFrequently: true });
        if (!ctx) return;

        ctx.drawImage(img, 0, 0, W, H);
        const imageData = ctx.getImageData(0, 0, W, H);
        const data = imageData.data;

        let totalLuma = 0;
        let skinLikePixels = 0;

        // Divide frame into a 4×2 grid of zones for spatial clustering
        const COLS = 4;
        const ROWS = 2;
        const zoneCounts: number[][] = Array.from({ length: ROWS }, () =>
          new Array(COLS).fill(0)
        );

        for (let i = 0; i < data.length; i += 4) {
          const r = data[i];
          const g = data[i + 1];
          const b = data[i + 2];
          const pixIdx = i / 4;
          const px = pixIdx % W;
          const py = Math.floor(pixIdx / W);

          // Luma calculation
          const luma = 0.299 * r + 0.587 * g + 0.114 * b;
          totalLuma += luma;

          // Skin-tone heuristic (handles varied ethnicities)
          const isSkin =
            r > 60 && g > 40 && b > 20 &&
            r > g && r > b &&
            Math.abs(r - g) > 10 &&
            r - b > 10 &&
            r < 250;

          if (isSkin) {
            skinLikePixels++;
            const col = Math.floor((px / W) * COLS);
            const row = Math.floor((py / H) * ROWS);
            zoneCounts[row][col]++;
          }
        }

        const totalPixels = data.length / 4;
        const avgLuma = totalLuma / totalPixels;
        const skinRatio = skinLikePixels / totalPixels;

        // Subject is present when room isn't completely dark and enough skin detected
        const isPresent = avgLuma > 12 && skinRatio > 0.04;
        setInternalFaceDetected(isPresent);
        onFacePresenceChange?.(isPresent);

        // ── Multiple-face detection ───────────────────────────────────────────
        // Count non-adjacent zones that have meaningful skin concentrations.
        // Threshold: zone must contain at least 1% of all skin pixels.
        const zoneThreshold = Math.max(1, skinLikePixels * 0.01);
        let activeCols: number[] = [];
        zoneCounts.forEach((row) => {
          row.forEach((count, col) => {
            if (count >= zoneThreshold && !activeCols.includes(col)) {
              activeCols.push(col);
            }
          });
        });

        // Two or more distinct horizontal regions → multiple faces detected
        const multipleFacesDetected = isPresent && activeCols.length >= 2;
        if (multipleFacesDetected) {
          onMultipleFacesDetected?.();
        }
      };
      img.src = screenshot;
    }, 2000);

    return () => clearInterval(interval);
  }, [camOn, webcamRef, onFacePresenceChange, onMultipleFacesDetected]);

  const isWarningActive = !camOn || !faceDetected || !internalFaceDetected;

  return (
    <div className="relative overflow-hidden rounded-[28px] border border-white/10 bg-[#1E293B] shadow-2xl backdrop-blur-xl">
      {/* ================= HEADER ================= */}
      <div className="absolute left-0 right-0 top-0 z-20 flex items-center justify-between p-5">
        <div className="flex items-center gap-2 rounded-full border border-red-500/30 bg-[#1E293B]/80 px-4 py-2 backdrop-blur-md">
          <span
            className={`h-3 w-3 rounded-full ${
              live ? "animate-pulse bg-red-500" : "bg-emerald-500"
            }`}
          />
          <span
            className={`font-semibold ${
              live ? "text-red-400" : "text-emerald-400"
            }`}
          >
            {live ? "REC LIVE" : "READY"}
          </span>
        </div>

        <div className="flex gap-3">
          <div className="rounded-full border border-white/10 bg-[#1E293B]/80 px-4 py-2 text-sm text-white font-mono">
            HD 1080p
          </div>
          <button className="rounded-full border border-white/10 bg-[#1E293B]/80 p-3 text-white transition hover:bg-[#4096ff]">
            <Maximize2 size={18} />
          </button>
        </div>
      </div>

      {/* ================= FACE MISSING WARNING OVERLAY ================= */}
      {isWarningActive && camOn && (
        <div className="absolute inset-x-0 top-16 z-30 mx-auto max-w-md animate-bounce rounded-2xl border border-red-500/50 bg-red-950/90 p-4 text-center text-red-200 shadow-2xl backdrop-blur-md">
          <div className="flex items-center justify-center gap-2 font-bold text-red-100">
            <AlertTriangle className="h-6 w-6 text-red-400" />
            <span>WARNING: Subject Away From Camera!</span>
          </div>
          <p className="mt-1 text-xs text-red-300">
            Please return to frame and face the camera directly. Violation logged.
          </p>
        </div>
      )}

      {/* ================= WEBCAM STAGE ================= */}
      <div className="relative h-[520px] w-full bg-[#0F172A]">
        {camOn ? (
          <>
            <Webcam
              ref={webcamRef}
              audio={false}
              mirrored
              screenshotFormat="image/jpeg"
              videoConstraints={{
                facingMode: "user",
                width: 1280,
                height: 720,
              }}
              className="h-full w-full object-cover"
            />
            {/* Facial Detection Scanning Bounding Frame */}
            <div
              className={`absolute inset-12 pointer-events-none rounded-3xl border-2 transition-colors duration-500 ${
                isWarningActive ? "border-red-500/70 bg-red-500/5" : "border-[#4096ff]/30"
              }`}
            >
              <div className="absolute top-2 left-3 text-[10px] uppercase font-mono tracking-widest text-slate-400">
                {isWarningActive ? "⚠️ Target Missing" : "✓ Subject Tracked"}
              </div>
            </div>
          </>
        ) : (
          <div className="flex h-full items-center justify-center">
            <div className="text-center text-slate-400">
              <VideoOff className="mx-auto h-16 w-16 text-slate-500" />
              <h3 className="mt-4 text-xl font-semibold text-white">Camera Disabled</h3>
              <p className="text-sm text-slate-400">Enable camera to proceed with interview</p>
            </div>
          </div>
        )}
      </div>

      {/* ================= FOOTER ================= */}
      <div className="flex items-center justify-between border-t border-white/10 bg-[#1E293B] px-6 py-5">
        <div>
          <h3 className="font-semibold text-white">Candidate Camera Preview</h3>
          <p className="text-sm text-slate-400 font-mono">Elapsed: {elapsed}</p>
        </div>

        <div className="flex gap-4">
          <button
            onClick={onToggleMic}
            className={`rounded-full p-3.5 text-white transition hover:bg-[#60a5fa] ${
              micOn ? "bg-[#4096ff]" : "bg-red-500"
            }`}
            title={micOn ? "Mute Microphone" : "Unmute Microphone"}
          >
            {micOn ? <Mic size={18} /> : <MicOff size={18} />}
          </button>

          <button
            onClick={onToggleCam}
            className={`rounded-full p-3.5 text-white transition hover:bg-[#60a5fa] ${
              camOn ? "bg-[#4096ff]" : "bg-red-500"
            }`}
            title={camOn ? "Disable Camera" : "Enable Camera"}
          >
            {camOn ? <Video size={18} /> : <VideoOff size={18} />}
          </button>
        </div>
      </div>
    </div>
  );
}