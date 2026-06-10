function ProbMiniBar({ home, draw, away }) {
  return (
    <div className="mt-2">
      <div className="flex h-1.5 rounded overflow-hidden w-full">
        <div style={{ width: `${home * 100}%` }} className="bg-wc-green" />
        <div style={{ width: `${draw * 100}%` }} className="bg-wc-dark" />
        <div style={{ width: `${away * 100}%` }} className="bg-wc-blue" />
      </div>
      <div className="flex items-center justify-center gap-3 mt-1.5">
        <span className="flex items-center gap-1 text-[11px] text-gray-500">
          <span className="inline-block w-2 h-2 rounded-[2px] bg-wc-green flex-none" />
          H {(home * 100).toFixed(0)}%
        </span>
        <span className="flex items-center gap-1 text-[11px] text-gray-500">
          <span className="inline-block w-2 h-2 rounded-[2px] bg-wc-dark flex-none" />
          D {(draw * 100).toFixed(0)}%
        </span>
        <span className="flex items-center gap-1 text-[11px] text-gray-500">
          <span className="inline-block w-2 h-2 rounded-[2px] bg-wc-blue flex-none" />
          A {(away * 100).toFixed(0)}%
        </span>
      </div>
    </div>
  );
}

function FixtureMeta({ date, city }) {
  const formatted = date
    ? new Date(date + "T00:00:00").toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" })
    : null;
  return (
    <div className="flex items-center justify-center gap-1.5 mt-1.5 text-[10px] text-gray-400">
      {formatted && <span>{formatted}</span>}
      {formatted && city && <span>·</span>}
      {city && <span>{city}</span>}
    </div>
  );
}

// actualScore: { home: number, away: number } | null | undefined
// When isActual=true and actualScore is null  → "Not played yet"
// When isActual=true and actualScore is set   → show the real score
// When isActual=false                         → show predicted score + prob bar
export default function MatchCard({ fixture, isActual = false, actualScore }) {
  if (isActual) {
    if (!actualScore) {
      return (
        <div className="bg-white rounded-lg p-3 border border-gray-200 shadow-sm">
          <div className="flex items-center justify-between gap-2">
            <span className="text-gray-600 text-xs font-medium flex-1 text-right truncate">
              {fixture.home_team}
            </span>
            <span
              className="text-[10px] text-gray-400 border border-gray-300 rounded px-2 py-1 whitespace-nowrap"
              data-testid="not-played-badge"
            >
              Not played yet
            </span>
            <span className="text-gray-600 text-xs font-medium flex-1 text-left truncate">
              {fixture.away_team}
            </span>
          </div>
          <FixtureMeta date={fixture.date} city={fixture.city} />
        </div>
      );
    }

    const { home: hg, away: ag } = actualScore;
    const winnerSide = hg > ag ? "home" : ag > hg ? "away" : null;

    return (
      <div className="bg-white rounded-lg p-3 border border-gray-200 shadow-sm">
        <div className="flex items-center justify-between gap-2">
          <span
            className={`text-xs font-semibold flex-1 text-right truncate ${
              winnerSide === "home" ? "text-wc-green" : "text-gray-600"
            }`}
          >
            {fixture.home_team}
          </span>
          <div className="flex items-center gap-1 px-2 py-0.5 bg-gray-100 rounded text-xs font-bold text-gray-800 whitespace-nowrap">
            <span>{hg}</span>
            <span className="text-gray-400">:</span>
            <span>{ag}</span>
          </div>
          <span
            className={`text-xs font-semibold flex-1 text-left truncate ${
              winnerSide === "away" ? "text-wc-green" : "text-gray-600"
            }`}
          >
            {fixture.away_team}
          </span>
        </div>
        <FixtureMeta date={fixture.date} city={fixture.city} />
      </div>
    );
  }

  // Predicted mode
  const predictedWinner =
    fixture.predicted_outcome === "home_win" ? "home" :
    fixture.predicted_outcome === "away_win" ? "away" : null;

  return (
    <div className="bg-white rounded-lg p-3 border border-gray-200 hover:border-gray-300 transition-colors shadow-sm">
      <div className="flex items-center justify-between gap-2">
        <span
          className={`text-xs font-semibold flex-1 text-right truncate ${
            predictedWinner === "home" ? "text-wc-green" : "text-gray-600"
          }`}
        >
          {fixture.home_team}
        </span>
        <div className="flex items-center gap-1 px-2 py-0.5 bg-gray-100 rounded text-xs font-bold text-gray-800 whitespace-nowrap">
          <span>{Math.round(fixture.predicted_home_goals)}</span>
          <span className="text-gray-400">:</span>
          <span>{Math.round(fixture.predicted_away_goals)}</span>
        </div>
        <span
          className={`text-xs font-semibold flex-1 text-left truncate ${
            predictedWinner === "away" ? "text-wc-green" : "text-gray-600"
          }`}
        >
          {fixture.away_team}
        </span>
      </div>
      <ProbMiniBar
        home={fixture.home_win_prob}
        draw={fixture.draw_prob}
        away={fixture.away_win_prob}
      />
      <FixtureMeta date={fixture.date} city={fixture.city} />
    </div>
  );
}
