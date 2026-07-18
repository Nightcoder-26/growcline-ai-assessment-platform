import { EventsTableProps } from "@/types/cheating";

const severityStyles = {
  Low: "bg-green-500/15 text-green-400",
  Medium: "bg-yellow-500/15 text-yellow-400",
  High: "bg-red-500/15 text-red-400",
};

export default function EventsTable({
  events,
}: EventsTableProps) {
  return (
    <section className="rounded-2xl border border-slate-700 bg-[#111827] p-6 shadow-lg">
      <h2 className="mb-6 text-xl font-semibold text-white">
        Suspicious Events
      </h2>

      <div className="overflow-x-auto">
        <table className="w-full text-left">
          <thead className="border-b border-slate-700">
            <tr>
              <th className="pb-3 text-sm font-medium text-slate-400">
                Time
              </th>

              <th className="pb-3 text-sm font-medium text-slate-400">
                Event
              </th>

              <th className="pb-3 text-sm font-medium text-slate-400">
                Severity
              </th>
            </tr>
          </thead>

          <tbody>
            {events.map((event) => (
              <tr
                key={event.id}
                className="border-b border-slate-800"
              >
                <td className="py-4 text-slate-300">
                  {event.time}
                </td>

                <td className="py-4 font-medium text-white">
                  {event.event}
                </td>

                <td className="py-4">
                  <span
                    className={`rounded-full px-3 py-1 text-xs font-medium ${
                      severityStyles[event.severity]
                    }`}
                  >
                    {event.severity}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}