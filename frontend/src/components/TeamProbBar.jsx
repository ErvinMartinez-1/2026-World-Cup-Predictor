const SEGMENTS = [
  { key: "r32_prob",     label: "R32",  color: "#474A4A" },
  { key: "r16_prob",     label: "R16",  color: "#2A398D" },
  { key: "quarter_prob", label: "QF",   color: "#3CAC3B" },
  { key: "semi_prob",    label: "SF",   color: "#3CAC3B" },
  { key: "final_prob",   label: "Final",color: "#E61D25" },
  { key: "win_prob",     label: "🏆",   color: "#FFD700" },
];

function ProbBar({ team }) {
  return (
    <div className="mb-4">
      <div className="flex justify-between items-center mb-1">
        <span className="text-gray-900 text-sm font-medium">{team.team}</span>
        <span className="text-yellow-400 text-sm font-bold">
          {(team.win_prob * 100).toFixed(1)}%
        </span>
      </div>
      <div className="flex h-5 rounded overflow-hidden w-full bg-gray-200">
        {SEGMENTS.map(({ key, label, color }) => {
          const pct = (team[key] ?? 0) * 100;
          return (
            <div
              key={key}
              className="flex items-center justify-center overflow-hidden transition-all duration-700 group relative"
              style={{ width: `${pct}%`, backgroundColor: color, minWidth: pct > 3 ? "auto" : 0 }}
              title={`${label}: ${pct.toFixed(1)}%`}
            >
              {pct > 8 && (
                <span className="text-[10px] text-white/80 font-semibold pointer-events-none">
                  {label}
                </span>
              )}
            </div>
          );
        })}
      </div>
      <div className="flex justify-between text-[10px] text-gray-400 mt-0.5">
        <span>Qualification</span>
        <span>Champion</span>
      </div>
    </div>
  );
}

export default function TeamProbBar({ teams, limit = 10 }) {
  if (!teams) return null;
  const top = [...teams]
    .sort((a, b) => b.win_prob - a.win_prob)
    .slice(0, limit);

  return (
    <div>
      {top.map((t) => (
        <ProbBar key={t.team} team={t} />
      ))}
      <div className="flex flex-wrap gap-x-4 gap-y-1 mt-4">
        {SEGMENTS.map(({ key, label, color }) => (
          <div key={key} className="flex items-center gap-1.5">
            <span
              className="w-3 h-3 rounded-sm inline-block"
              style={{ backgroundColor: color }}
            />
            <span className="text-[11px] text-gray-500">{label}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
