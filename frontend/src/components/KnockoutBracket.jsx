import { ISO_MAP, NATION_COLORS, flagSrc } from "../utils/teamData";

const ROUNDS = [
  { key: "round_of_32",    label: "Round of 32",   cols: 16 },
  { key: "round_of_16",    label: "Round of 16",   cols: 8  },
  { key: "quarter_finals", label: "Quarterfinals", cols: 4  },
  { key: "semi_finals",    label: "Semifinals",    cols: 2  },
  { key: "final",          label: "Final",         cols: 1  },
];

const BRACKET_HEIGHT = 960;
const MATCH_CARD_H   = 76;
const COL_W          = 176;

// ─── Actual Knockout Results ──────────────────────────────────────────────────
// Fill in each match as it is played. Set home_team / away_team once the
// advancing teams are known, then add home_goals / away_goals / winner / method
// when the result is in. Leave fields as null until then.
// method: null | "extra_time" | "penalties"
const ACTUAL_KNOCKOUT = {
  round_of_32: [
    { id: "r32_1",  home_team: null, away_team: null, home_goals: null, away_goals: null, winner: null, method: null },
    { id: "r32_2",  home_team: null, away_team: null, home_goals: null, away_goals: null, winner: null, method: null },
    { id: "r32_3",  home_team: null, away_team: null, home_goals: null, away_goals: null, winner: null, method: null },
    { id: "r32_4",  home_team: null, away_team: null, home_goals: null, away_goals: null, winner: null, method: null },
    { id: "r32_5",  home_team: null, away_team: null, home_goals: null, away_goals: null, winner: null, method: null },
    { id: "r32_6",  home_team: null, away_team: null, home_goals: null, away_goals: null, winner: null, method: null },
    { id: "r32_7",  home_team: null, away_team: null, home_goals: null, away_goals: null, winner: null, method: null },
    { id: "r32_8",  home_team: null, away_team: null, home_goals: null, away_goals: null, winner: null, method: null },
    { id: "r32_9",  home_team: null, away_team: null, home_goals: null, away_goals: null, winner: null, method: null },
    { id: "r32_10", home_team: null, away_team: null, home_goals: null, away_goals: null, winner: null, method: null },
    { id: "r32_11", home_team: null, away_team: null, home_goals: null, away_goals: null, winner: null, method: null },
    { id: "r32_12", home_team: null, away_team: null, home_goals: null, away_goals: null, winner: null, method: null },
    { id: "r32_13", home_team: null, away_team: null, home_goals: null, away_goals: null, winner: null, method: null },
    { id: "r32_14", home_team: null, away_team: null, home_goals: null, away_goals: null, winner: null, method: null },
    { id: "r32_15", home_team: null, away_team: null, home_goals: null, away_goals: null, winner: null, method: null },
    { id: "r32_16", home_team: null, away_team: null, home_goals: null, away_goals: null, winner: null, method: null },
  ],
  round_of_16: [
    { id: "r16_1", home_team: null, away_team: null, home_goals: null, away_goals: null, winner: null, method: null },
    { id: "r16_2", home_team: null, away_team: null, home_goals: null, away_goals: null, winner: null, method: null },
    { id: "r16_3", home_team: null, away_team: null, home_goals: null, away_goals: null, winner: null, method: null },
    { id: "r16_4", home_team: null, away_team: null, home_goals: null, away_goals: null, winner: null, method: null },
    { id: "r16_5", home_team: null, away_team: null, home_goals: null, away_goals: null, winner: null, method: null },
    { id: "r16_6", home_team: null, away_team: null, home_goals: null, away_goals: null, winner: null, method: null },
    { id: "r16_7", home_team: null, away_team: null, home_goals: null, away_goals: null, winner: null, method: null },
    { id: "r16_8", home_team: null, away_team: null, home_goals: null, away_goals: null, winner: null, method: null },
  ],
  quarter_finals: [
    { id: "qf_1", home_team: null, away_team: null, home_goals: null, away_goals: null, winner: null, method: null },
    { id: "qf_2", home_team: null, away_team: null, home_goals: null, away_goals: null, winner: null, method: null },
    { id: "qf_3", home_team: null, away_team: null, home_goals: null, away_goals: null, winner: null, method: null },
    { id: "qf_4", home_team: null, away_team: null, home_goals: null, away_goals: null, winner: null, method: null },
  ],
  semi_finals: [
    { id: "sf_1", home_team: null, away_team: null, home_goals: null, away_goals: null, winner: null, method: null },
    { id: "sf_2", home_team: null, away_team: null, home_goals: null, away_goals: null, winner: null, method: null },
  ],
  final: { id: "final", home_team: null, away_team: null, home_goals: null, away_goals: null, winner: null, method: null },
};
// ─────────────────────────────────────────────────────────────────────────────

function TeamRow({ team, isWinner, goals, isBottom }) {
  const code = team ? ISO_MAP[team] : null;
  const isBlank = !team;
  return (
    <div
      className={`flex items-center justify-between px-2 py-1.5 ${
        isBottom ? "" : "border-b border-gray-100"
      } ${isWinner ? "bg-wc-green/8" : ""}`}
    >
      <div className="flex items-center gap-1.5 flex-1 min-w-0">
        {code && (
          <img
            src={flagSrc(code, 40)}
            alt=""
            loading="lazy"
            style={{
              width: 16, height: 11, objectFit: "cover",
              borderRadius: 2, flexShrink: 0,
              boxShadow: "0 0 0 1px rgba(15,23,42,0.08)",
            }}
          />
        )}
        {isBlank && (
          <span className="w-4 h-2.5 rounded-sm bg-gray-200 flex-shrink-0" />
        )}
        <span
          className={`text-xs font-medium truncate ${
            isBlank ? "text-gray-300 italic" :
            isWinner ? "text-wc-green font-semibold" : "text-gray-500"
          }`}
        >
          {isWinner && <span className="mr-0.5">✓</span>}
          {isBlank ? "TBD" : team}
        </span>
      </div>
      <span className={`text-xs font-bold ml-1.5 tabular-nums ${isWinner ? "text-wc-green" : "text-gray-300"}`}>
        {goals ?? "–"}
      </span>
    </div>
  );
}

function KnockoutMatch({ match }) {
  if (!match) {
    return <div className="h-[76px] w-full bg-gray-100 rounded-lg border border-dashed border-gray-300" />;
  }

  const winner     = match.winner;
  const method     = match.method;
  const methodLabel = method === "extra_time" ? "AET" : method === "penalties" ? "PEN" : null;

  return (
    <div className="w-full bg-white rounded-lg border border-gray-200 hover:border-gray-300 transition-colors overflow-hidden shadow-sm">
      <TeamRow team={match.home_team} isWinner={match.home_team != null && match.home_team === winner} goals={match.home_goals} isBottom={false} />
      <TeamRow team={match.away_team} isWinner={match.away_team != null && match.away_team === winner} goals={match.away_goals} isBottom={true} />
      {methodLabel && (
        <div className="text-center text-[10px] text-gray-300 py-0.5 bg-gray-50">{methodLabel}</div>
      )}
    </div>
  );
}

function RoundColumn({ label, matches }) {
  const count = matches.length;
  const itemHeight = BRACKET_HEIGHT / count;

  return (
    <div className="flex flex-col" style={{ width: COL_W, minWidth: COL_W }}>
      <div className="text-center text-[11px] font-bold text-gray-400 uppercase tracking-wider mb-3 pb-2 border-b border-gray-200">
        {label}
      </div>
      <div className="relative flex flex-col" style={{ height: BRACKET_HEIGHT }}>
        {matches.map((match, i) => (
          <div
            key={i}
            className="absolute left-0 right-0 flex items-center"
            style={{ top: i * itemHeight + (itemHeight - MATCH_CARD_H) / 2, height: MATCH_CARD_H }}
          >
            <KnockoutMatch match={match} />
          </div>
        ))}
      </div>
    </div>
  );
}

function ChampionCard({ winner }) {
  const code   = ISO_MAP[winner];
  const colors = NATION_COLORS[winner] ?? { bg: "#1a3a5c", accent: "#FFD700" };

  return (
    <div className="flex flex-col" style={{ width: 156, minWidth: 156 }}>
      <div className="text-center text-[11px] font-bold text-gray-400 uppercase tracking-wider mb-3 pb-2 border-b border-gray-200 w-full">
        Champion
      </div>
      <div
        className="flex flex-col items-center justify-center gap-4 rounded-xl border-2 p-4 w-full"
        style={{
          height: BRACKET_HEIGHT,
          background: `linear-gradient(160deg, ${colors.bg}ee 0%, ${colors.bg}bb 100%)`,
          borderColor: colors.accent + "99",
        }}
        data-testid="champion-card"
      >
        {code && (
          <img
            src={flagSrc(code, 160)}
            alt={winner}
            style={{
              width: 96, height: 64, objectFit: "cover",
              borderRadius: 6,
              boxShadow: "0 6px 24px rgba(0,0,0,0.45)",
            }}
          />
        )}
        <div className="font-bold text-sm text-center leading-tight px-1" style={{ color: colors.accent }}>
          {winner}
        </div>
        <div className="text-[10px] uppercase tracking-widest text-center" style={{ color: colors.accent + "99" }}>
          Predicted
        </div>
      </div>
    </div>
  );
}

function ActualChampionCard() {
  return (
    <div className="flex flex-col" style={{ width: 156, minWidth: 156 }}>
      <div className="text-center text-[11px] font-bold text-gray-400 uppercase tracking-wider mb-3 pb-2 border-b border-gray-200 w-full">
        Champion
      </div>
      <div
        className="flex flex-col items-center justify-center gap-3 rounded-xl border-2 border-dashed border-gray-300 bg-gray-50 p-4 w-full"
        style={{ height: BRACKET_HEIGHT }}
      >
        <div className="w-16 h-11 rounded bg-gray-200" />
        <div className="text-gray-300 text-xs italic font-medium">TBD</div>
      </div>
    </div>
  );
}

export default function KnockoutBracket({ data, isActual }) {
  if (!data) {
    return (
      <div className="flex gap-4 overflow-x-auto pb-4">
        {ROUNDS.map((r) => (
          <div
            key={r.key}
            className="rounded-xl bg-gray-100 animate-pulse"
            style={{ width: COL_W, minWidth: COL_W, height: BRACKET_HEIGHT + 40 }}
          />
        ))}
      </div>
    );
  }

  function asArray(val) {
    if (!val) return [];
    return Array.isArray(val) ? val : [val];
  }

  if (isActual) {
    return (
      <div className="overflow-x-auto pb-6" data-testid="knockout-bracket-actual">
        <div className="flex gap-3 w-fit mx-auto">
          {ROUNDS.map(({ key, label }) => (
            <RoundColumn
              key={key}
              label={label}
              matches={asArray(ACTUAL_KNOCKOUT[key])}
            />
          ))}
          <ActualChampionCard />
        </div>
      </div>
    );
  }

  const knockout = data.knockout ?? {};
  const winner   = data.winner;

  return (
    <div className="overflow-x-auto pb-6" data-testid="knockout-bracket">
      <div className="flex gap-3 w-fit ml-auto">
        {ROUNDS.map(({ key, label }) => (
          <RoundColumn
            key={key}
            label={label}
            matches={asArray(knockout[key])}
          />
        ))}
        {winner && <ChampionCard winner={winner} />}
      </div>
    </div>
  );
}
