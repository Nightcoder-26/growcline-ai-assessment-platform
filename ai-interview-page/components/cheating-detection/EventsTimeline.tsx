import { Clock3, AlertTriangle } from "lucide-react";
import { EventsTimelineProps } from "@/types/cheating";

const severityColors = {
  Low: "bg-green-500",
  Medium: "bg-yellow-500",
  High: "bg-red-500",
};

export default function EventsTimeline({
  events,
}: EventsTimelineProps) {
  return (
    <section className="rounded-2xl border border-slate-700 bg-[#111827] p-6 shadow-lg">
      <div className="mb-6 flex items-center gap-2">
        <Clock3 className="text-[#4096FF]" size={22} />
        <h2 className="text-xl font-semibold text-white">
          Recent Events
        </h2>
      </div>

      <div className="space-y-4">
        {events.map((event) => (
          <div
            key={event.id}
            className="flex items-start gap-4 rounded-lg border border-slate-700 bg-[#0F172A] p-4"
          >
            <div
              className={`mt-1 h-3 w-3 rounded-full ${
                severityColors[event.severity]
              }`}
            />

            <div className="flex-1">
              <div className="flex items-center justify-between">
                <p className="font-medium text-white">
                  {event.event}
                </p>

                <span className="text-sm text-slate-400">
                  {event.time}
                </span>
              </div>

              <div className="mt-2 flex items-center gap-2">
                <AlertTriangle
                  size={14}
                  className="text-yellow-400"
                />

                <span className="text-sm text-slate-400">
                  Severity: {event.severity}
                </span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}