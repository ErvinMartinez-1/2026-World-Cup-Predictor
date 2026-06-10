import { ISO_MAP, flagSrc } from "../utils/teamData";

const STAGE_COLS = [
  { key: "r32_prob",     label: "R32", color: "#474A4A" },
  { key: "r16_prob",     label: "R16", color: "#2A398D" },
  { key: "quarter_prob", label: "QF",  color: "#3CAC3B" },
  { key: "semi_prob",    label: "SF",  color: "#3CAC3B" },
  { key: "final_prob",   label: "F",   color: "#E61D25" },
];

const WIN_COLOR = "#FFD700";

// grid: rank | team | R32 | R16 | QF | SF | F | Win
const GRID = "20px 1fr repeat(5, 30px) 50px";

function fmtPct(val) {
  const p = (val ?? 0) * 100;
  if (p === 0)  return "—";
  if (p < 1)    return "<1";
  return `${Math.round(p)}%`;
}

function ProbRow({ team, rank }) {
  const code = ISO_MAP[team.team];
  return (
    <div
      className="grid items-center py-[5px] border-b border-gray-50 last:border-0 hover:bg-gray-50/70 rounded-sm transition-colors"
      style={{ gridTemplateColumns: GRID, columnGap: 4 }}
    >
      {/* Rank */}
      <span className="text-[9px] text-gray-300 text-right tabular-nums pr-0.5">{rank}</span>

      {/* Flag + name */}
      <div className="flex items-center gap-1.5 min-w-0">
        {code ? (
          <img
            src={flagSrc(code, 40)}
            alt=""
            loading="lazy"
            style={{
              width: 18, height: 12, objectFit: "cover",
              borderRadius: 2, flexShrink: 0,
              boxShadow: "0 0 0 1px rgba(15,23,42,0.08)",
            }}
          />
        ) : (
          <span className="w-[18px] h-3 rounded bg-gray-200 flex-shrink-0" />
        )}
        <span className="text-xs font-medium text-gray-800 truncate">{team.team}</span>
      </div>

      {/* Stage odds — colored per round */}
      {STAGE_COLS.map(({ key, color }) => (
        <div key={key} className="text-center">
          <span className="text-[11px] font-medium tabular-nums" style={{ color }}>
            {fmtPct(team[key])}
          </span>
        </div>
      ))}

      {/* Championship — biggest */}
      <span
        className="text-sm font-bold tabular-nums text-right pr-0.5"
        style={{ color: WIN_COLOR }}
      >
        {(team.win_prob * 100).toFixed(1)}%
      </span>
    </div>
  );
}

export default function TeamProbBar({ teams }) {
  if (!teams) return null;
  const sorted = [...teams].sort((a, b) => b.win_prob - a.win_prob);

  return (
    <div className="overflow-y-auto" style={{ maxHeight: "calc(100vh - 250px)" }}>
      {/* Sticky header — lives inside the scroll container so widths always match */}
      <div
        className="grid items-center sticky top-0 bg-white z-10 pb-1.5 pt-0.5 mb-1 border-b border-gray-200"
        style={{ gridTemplateColumns: GRID, columnGap: 4 }}
      >
        <span />
        <span className="text-[8px] font-bold text-gray-400 uppercase tracking-wide">Team</span>
        {STAGE_COLS.map(({ label, color }) => (
          <div key={label} className="text-center">
            <span className="text-[11px] font-bold uppercase tracking-wide" style={{ color }}>
              {label}
            </span>
          </div>
        ))}
        <div className="text-right pr-0.5">
          <span className="text-[11px] font-bold uppercase tracking-wide" style={{ color: WIN_COLOR }}>
            Win
          </span>
        </div>
      </div>

      {sorted.map((t, i) => (
        <ProbRow key={t.team} team={t} rank={i + 1} />
      ))}
    </div>
  );
}
