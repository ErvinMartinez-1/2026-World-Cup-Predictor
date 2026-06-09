const ROUNDS = [
  { key: "round_of_32",    label: "Round of 32",  cols: 16 },
  { key: "round_of_16",    label: "Round of 16",  cols: 8 },
  { key: "quarter_finals", label: "Quarterfinals", cols: 4 },
  { key: "semi_finals",    label: "Semifinals",    cols: 2 },
  { key: "final",          label: "Final",         cols: 1 },
];

const BRACKET_HEIGHT = 960;
const MATCH_CARD_H = 72;

function KnockoutMatch({ match, isActual }) {
  if (!match) return <div className="h-[72px] bg-gray-100 rounded-lg border border-dashed border-gray-300" />;

  const winner = match.winner;
  const method = match.method;
  const score = match.predicted_score;
  const homeGoals = isActual ? match.home_goals : match.home_goals;
  const awayGoals = isActual ? match.away_goals : match.away_goals;

  const methodLabel = method === "extra_time" ? "AET" : method === "penalties" ? "PEN" : null;

  return (
    <div className="bg-white rounded-lg border border-gray-200 hover:border-gray-300 transition-colors overflow-hidden shadow-sm">
      <div className="flex flex-col">
        {[match.home_team, match.away_team].map((team, i) => {
          const goals = i === 0 ? homeGoals : awayGoals;
          const isWinner = team === winner;
          return (
            <div
              key={team}
              className={`flex items-center justify-between px-3 py-1.5 ${
                i === 0 ? "border-b border-gray-100" : ""
              } ${isWinner ? "bg-wc-green/8" : ""}`}
            >
              <span
                className={`text-xs font-medium truncate flex-1 ${
                  isWinner ? "text-wc-green font-semibold" : "text-gray-500"
                }`}
              >
                {isWinner && <span className="mr-1">✓</span>}
                {team}
              </span>
              <span
                className={`text-xs font-bold ml-2 ${
                  isWinner ? "text-wc-green" : "text-gray-400"
                }`}
              >
                {goals ?? "–"}
              </span>
            </div>
          );
        })}
      </div>
      {methodLabel && (
        <div className="text-center text-[10px] text-gray-300 py-0.5 bg-gray-50">
          {methodLabel}
        </div>
      )}
    </div>
  );
}

function RoundColumn({ roundKey, label, matches, isActual }) {
  const count = matches.length;
  const itemHeight = BRACKET_HEIGHT / count;

  return (
    <div className="flex flex-col" style={{ width: 160, minWidth: 160 }}>
      <div className="text-center text-[11px] font-bold text-gray-400 uppercase tracking-wider mb-3 pb-2 border-b border-gray-200">
        {label}
      </div>
      <div
        className="relative flex flex-col"
        style={{ height: BRACKET_HEIGHT }}
      >
        {matches.map((match, i) => (
          <div
            key={i}
            className="absolute left-0 right-0 flex items-center"
            style={{
              top: i * itemHeight + (itemHeight - MATCH_CARD_H) / 2,
              height: MATCH_CARD_H,
            }}
          >
            <KnockoutMatch match={match} isActual={isActual} />
          </div>
        ))}
      </div>
    </div>
  );
}

function ChampionCard({ winner }) {
  return (
    <div className="flex flex-col items-center justify-center" style={{ width: 140, minWidth: 140 }}>
      <div className="text-center text-[11px] font-bold text-gray-400 uppercase tracking-wider mb-3 pb-2 border-b border-gray-200 w-full">
        Champion
      </div>
      <div
        className="flex flex-col items-center justify-center gap-3 rounded-xl border-2 border-yellow-500/60 bg-yellow-500/5 p-4 w-full"
        style={{ height: BRACKET_HEIGHT }}
        data-testid="champion-card"
      >
        <span
          className="text-5xl"
          style={{ filter: "drop-shadow(0 0 16px rgba(255,215,0,0.6))" }}
          aria-hidden="true"
        >
          🏆
        </span>
        <div className="text-yellow-400 font-bold text-sm text-center leading-tight">
          {winner}
        </div>
        <div className="text-yellow-500/40 text-[10px] uppercase tracking-widest">
          Predicted
        </div>
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
            style={{ width: 160, minWidth: 160, height: BRACKET_HEIGHT + 40 }}
          />
        ))}
      </div>
    );
  }

  const knockout = data.knockout ?? {};
  const winner = data.winner;

  // The API returns `final` as a plain object, all other rounds as arrays.
  // Normalise everything to arrays so RoundColumn always receives an array.
  function asArray(val) {
    if (!val) return [];
    return Array.isArray(val) ? val : [val];
  }

  return (
    <div className="overflow-x-auto pb-6" data-testid="knockout-bracket">
      <div className="flex gap-3 min-w-max">
        {ROUNDS.map(({ key, label }) => {
          const matches = asArray(knockout[key]);
          return (
            <RoundColumn
              key={key}
              roundKey={key}
              label={label}
              matches={matches}
              isActual={isActual}
            />
          );
        })}
        {winner && !isActual && <ChampionCard winner={winner} />}
      </div>
    </div>
  );
}
