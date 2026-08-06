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
} from "lucide-react";

// ---------------------------------------------------------------------------
// Detection configuration
// ---------------------------------------------------------------------------

/** How long face must be ABSENT before confirming face-missing violation (ms) */
const FACE_MISSING_CONFIRM_MS  = 3_000;
/** How long multiple-face must persist before confirming violation (ms) */
const MULTIPLE_FACE_CONFIRM_MS = 3_000;
/** How often to run the canvas face analysis (ms) */
const ANALYSIS_INTERVAL_MS     = 1_000;

// ---------------------------------------------------------------------------
// Props
// ---------------------------------------------------------------------------

interface VideoStageProps {
  webcamRef:   React.RefObject<Webcam | null>;
  recording:   boolean;
  paused:      boolean;
  camOn:       boolean;
  micOn:       boolean;
  elapsed:     string;
  take:        number;
  faceDetected?: boolean;
  onToggleCam: () => void;
  onToggleMic: () => void;
  /**
   * Called when the DISPLAY status of face presence changes.
   * Called unconditionally (not guarded by recording) so UI always reflects
   * the real camera state.
   * VIOLATION event is only fired if recording === true.
   */
  onFacePresenceChange?: (detected: boolean) => void;
  /**
   * Called when multiple faces are CONFIRMED in frame.
   * Only fires when recording === true.
   */
  onMultipleFacesDetected?: () => void;
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

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

  // Offscreen canvas for pixel analysis
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  // Internal detected state (for UI display — always reflects real camera)
  const [internalFaceDetected, setInternalFaceDetected] = useState(true);

  // ── Temporal state machines ───────────────────────────────────────────────

  // Face missing state
  type FaceState = "NORMAL" | "PENDING_MISSING" | "ACTIVE_MISSING";
  const faceStateRef     = useRef<FaceState>("NORMAL");
  const missingSinceRef  = useRef<number | null>(null);

  // Multiple faces state
  type MultiState = "NORMAL" | "PENDING_MULTIPLE" | "ACTIVE_MULTIPLE";
  const multiStateRef    = useRef<MultiState>("NORMAL");
  const multipleSinceRef = useRef<number | null>(null);

  // Keep a ref to the recording flag so the interval callback always reads current value
  const recordingRef = useRef(recording);
  useEffect(() => { recordingRef.current = recording; }, [recording]);

  // ── Reset detector state when camera is toggled ───────────────────────────
  useEffect(() => {
    if (!camOn) {
      faceStateRef.current = "ACTIVE_MISSING";
      multiStateRef.current = "NORMAL";
      missingSinceRef.current = null;
      multipleSinceRef.current = null;
      setInternalFaceDetected(false);
      onFacePresenceChange?.(false);
    } else {
      faceStateRef.current = "NORMAL";
      multiStateRef.current = "NORMAL";
      missingSinceRef.current = null;
      multipleSinceRef.current = null;
      setInternalFaceDetected(true);
      onFacePresenceChange?.(true);
    }
  }, [camOn, onFacePresenceChange]);

  // ── Canvas-based face presence + multiple-face analysis ───────────────────
  useEffect(() => {
    if (!camOn) return;

    const interval = setInterval(() => {
      const wc = webcamRef.current;
      if (!wc) return;

      const screenshot = wc.getScreenshot();
      if (!screenshot) return;

      const img = new Image();
      img.onload = () => {
        // Lazy-create offscreen canvas
        if (!canvasRef.current) {
          canvasRef.current = document.createElement("canvas");
        }
        const canvas = canvasRef.current;
        const W = 160;
        const H = 90;
        canvas.width  = W;
        canvas.height = H;

        const ctx = canvas.getContext("2d", { willReadFrequently: true });
        if (!ctx) return;

        ctx.drawImage(img, 0, 0, W, H);
        const { data } = ctx.getImageData(0, 0, W, H);

        const totalPixels    = (W * H);
        let   totalLuma      = 0;
        let   skinLikePixels = 0;
        const colSkinCounts  = new Array(16).fill(0);

        for (let i = 0; i < data.length; i += 4) {
          const r = data[i];
          const g = data[i + 1];
          const b = data[i + 2];

          totalLuma += 0.299 * r + 0.587 * g + 0.114 * b;

          // Skin-tone heuristic (works for a wide range of skin tones under webcam lighting)
          const isSkin =
            r > 60  && g > 35  && b > 15  &&
            r > g   && r > b   &&
            (r - g) > 10       &&
            (r - b) > 10       &&
            r < 250;

          if (isSkin) {
            skinLikePixels++;
            const px     = (i / 4) % W;
            const colBin = Math.min(15, Math.floor((px / W) * 16));
            colSkinCounts[colBin]++;
          }
        }

        const avgLuma   = totalLuma / totalPixels;
        const skinRatio = skinLikePixels / totalPixels;

        // A subject is considered present if the image is adequately lit AND
        // has a reasonable amount of skin-tone content.
        const isPresent = avgLuma > 12 && skinRatio > 0.03;

        const now = Date.now();

        // ── Face Missing State Machine ──────────────────────────────────────
        if (!isPresent) {
          if (faceStateRef.current === "NORMAL") {
            faceStateRef.current = "PENDING_MISSING";
            missingSinceRef.current = now;
            // Immediately update UI display (not a violation yet)
            setInternalFaceDetected(false);
            onFacePresenceChange?.(false);
          } else if (faceStateRef.current === "PENDING_MISSING") {
            if (
              missingSinceRef.current !== null &&
              now - missingSinceRef.current >= FACE_MISSING_CONFIRM_MS
            ) {
              faceStateRef.current = "ACTIVE_MISSING";
              console.log("[PROCTOR] FACE_MISSING confirmed");
              // Only fire a violation if we're actively recording
              if (recordingRef.current) {
                console.log("[PROCTOR] reporting FACE_MISSING (via onFacePresenceChange)");
                // onFacePresenceChange(false) is also what triggers logEvent("NO_FACE") in the parent
                // It was already called at PENDING transition for UI; parent's logEvent guards itself
              }
            }
          }
          // ACTIVE_MISSING: already notified, do nothing until face returns
        } else {
          // Face is present
          if (faceStateRef.current !== "NORMAL") {
            faceStateRef.current    = "NORMAL";
            missingSinceRef.current = null;
            setInternalFaceDetected(true);
            onFacePresenceChange?.(true);
            console.log("[PROCTOR] face returned, resetting face-missing state");
          }
        }

        // ── Multiple Faces State Machine ────────────────────────────────────

        // Spatial peak analysis: smooth the 16-column skin-count histogram
        // and detect ≥2 distinct peaks separated by a genuine valley.
        const smoothed = new Array(16).fill(0);
        for (let c = 0; c < 16; c++) {
          const prev = c > 0  ? colSkinCounts[c - 1] : colSkinCounts[c];
          const next = c < 15 ? colSkinCounts[c + 1] : colSkinCounts[c];
          smoothed[c] = prev * 0.25 + colSkinCounts[c] * 0.5 + next * 0.25;
        }

        // Thresholds relative to frame size
        const peakMin   = Math.max(10, totalPixels * 0.010);
        const valleyMax = Math.max(3,  totalPixels * 0.003);

        let peaksCount = 0;
        let inPeak     = false;
        let valleyGap  = 0;

        for (let c = 0; c < 16; c++) {
          if (smoothed[c] >= peakMin) {
            if (!inPeak) {
              if (peaksCount === 0 || valleyGap >= 3) {
                peaksCount++;
                inPeak    = true;
                valleyGap = 0;
              }
            }
          } else if (smoothed[c] <= valleyMax) {
            if (inPeak) inPeak = false;
            valleyGap++;
          }
        }

        const multipleFacesDetected = isPresent && peaksCount >= 2;

        if (multipleFacesDetected) {
          if (multiStateRef.current === "NORMAL") {
            multiStateRef.current   = "PENDING_MULTIPLE";
            multipleSinceRef.current = now;
          } else if (multiStateRef.current === "PENDING_MULTIPLE") {
            if (
              multipleSinceRef.current !== null &&
              now - multipleSinceRef.current >= MULTIPLE_FACE_CONFIRM_MS
            ) {
              multiStateRef.current = "ACTIVE_MULTIPLE";
              console.log("[PROCTOR] MULTIPLE_FACES confirmed");
              // Only fire violation if recording is active
              if (recordingRef.current) {
                console.log("[PROCTOR] reporting MULTIPLE_FACES");
                onMultipleFacesDetected?.();
              }
            }
          }
          // ACTIVE_MULTIPLE: violation already sent, stay quiet until reset
        } else {
          if (multiStateRef.current !== "NORMAL") {
            multiStateRef.current    = "NORMAL";
            multipleSinceRef.current = null;
            console.log("[PROCTOR] multiple-face condition cleared");
          }
        }
      };

      img.src = screenshot;
    }, ANALYSIS_INTERVAL_MS);

    return () => clearInterval(interval);
  }, [camOn, webcamRef, onFacePresenceChange, onMultipleFacesDetected]);

  // ── Derived display ───────────────────────────────────────────────────────

  // The warning overlay appears when the camera is on but no face is detected
  const showFaceWarning = camOn && (!faceDetected || !internalFaceDetected);

  // ── Render ────────────────────────────────────────────────────────────────

  return (
    <div className="relative overflow-hidden rounded-[28px] border border-white/10 bg-[#1E293B] shadow-2xl backdrop-blur-xl">

      {/* ── Header ── */}
      <div className="absolute left-0 right-0 top-0 z-20 flex items-center justify-between p-5">
        <div className="flex items-center gap-2 rounded-full border border-red-500/30 bg-[#1E293B]/80 px-4 py-2 backdrop-blur-md">
          <span
            className={`h-3 w-3 rounded-full ${
              live ? "animate-pulse bg-red-500" : "bg-emerald-500"
            }`}
          />
          <span className={`font-semibold ${live ? "text-red-400" : "text-emerald-400"}`}>
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

      {/* ── Face Warning Overlay ── */}
      {showFaceWarning && (
        <div className="absolute inset-x-0 top-16 z-30 mx-auto max-w-md rounded-2xl border border-red-500/50 bg-red-950/90 p-4 text-center shadow-2xl backdrop-blur-md animate-pulse">
          <div className="flex items-center justify-center gap-2 font-bold text-red-100">
            <AlertTriangle className="h-6 w-6 text-red-400" />
            <span>WARNING: Subject Away From Camera!</span>
          </div>
          <p className="mt-1 text-xs text-red-300">
            Please return to frame. Absence will be logged as a violation after the confirmation window.
          </p>
        </div>
      )}

      {/* ── Webcam Stage ── */}
      <div className="relative h-[520px] w-full bg-[#0F172A]">
        {camOn ? (
          <>
            <Webcam
              ref={webcamRef}
              audio={false}
              mirrored
              screenshotFormat="image/jpeg"
              videoConstraints={{ facingMode: "user", width: 1280, height: 720 }}
              className="h-full w-full object-cover"
            />

            {/* Detection scanning frame */}
            <div
              className={`absolute inset-12 pointer-events-none rounded-3xl border-2 transition-colors duration-500 ${
                showFaceWarning
                  ? "border-red-500/70 bg-red-500/5"
                  : "border-[#4096ff]/30"
              }`}
            >
              <div className="absolute top-2 left-3 text-[10px] uppercase font-mono tracking-widest text-slate-400">
                {showFaceWarning ? "⚠️ Target Missing" : "✓ Subject Tracked"}
              </div>
            </div>
          </>
        ) : (
          <div className="flex h-full items-center justify-center">
            <div className="text-center">
              <VideoOff className="mx-auto h-16 w-16 text-slate-500" />
              <h3 className="mt-4 text-xl font-semibold text-white">Camera Disabled</h3>
              <p className="text-sm text-slate-400">Enable camera to proceed with interview</p>
            </div>
          </div>
        )}
      </div>

      {/* ── Footer ── */}
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