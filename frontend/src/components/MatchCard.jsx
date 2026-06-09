function ProbMiniBar({ home, draw, away }) {
  return (
    <div className="flex h-1.5 rounded overflow-hidden mt-2 w-full" title={`H:${(home*100).toFixed(0)}% D:${(draw*100).toFixed(0)}% A:${(away*100).toFixed(0)}%`}>
      <div style={{ width: `${home * 100}%` }} className="bg-wc-green" />
      <div style={{ width: `${draw * 100}%` }} className="bg-wc-dark" />
      <div style={{ width: `${away * 100}%` }} className="bg-wc-blue" />
    </div>
  );
}

export default function MatchCard({ fixture, isActual = false }) {
  const hasActual = fixture.actual_home_goals !== null && fixture.actual_home_goals !== undefined;
  const predictedWinner =
    fixture.predicted_outcome === "home_win"
      ? "home"
      : fixture.predicted_outcome === "away_win"
      ? "away"
      : null;

  if (isActual && !hasActual) {
    return (
      <div className="bg-white rounded-lg p-3 border border-gray-200 flex items-center justify-between gap-2 shadow-sm">
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
    );
  }

  const homeGoals = isActual ? fixture.actual_home_goals : fixture.predicted_home_goals;
  const awayGoals = isActual ? fixture.actual_away_goals : fixture.predicted_away_goals;
  const homeScore = isActual ? homeGoals : Math.round(fixture.predicted_home_goals);
  const awayScore = isActual ? awayGoals : Math.round(fixture.predicted_away_goals);

  const actualWinner =
    isActual && hasActual
      ? homeGoals > awayGoals
        ? "home"
        : awayGoals > homeGoals
        ? "away"
        : null
      : null;

  const winnerSide = isActual ? actualWinner : predictedWinner;

  return (
    <div className="bg-white rounded-lg p-3 border border-gray-200 hover:border-gray-300 transition-colors shadow-sm">
      <div className="flex items-center justify-between gap-2">
        <span
          className={`text-xs font-semibold flex-1 text-right truncate ${
            winnerSide === "home" ? "text-wc-green" : "text-gray-600"
          }`}
        >
          {fixture.home_team}
        </span>
        <div className="flex items-center gap-1 px-2 py-0.5 bg-gray-100 rounded text-xs font-bold text-gray-800 whitespace-nowrap">
          <span>{homeScore ?? "–"}</span>
          <span className="text-gray-400">:</span>
          <span>{awayScore ?? "–"}</span>
        </div>
        <span
          className={`text-xs font-semibold flex-1 text-left truncate ${
            winnerSide === "away" ? "text-wc-green" : "text-gray-600"
          }`}
        >
          {fixture.away_team}
        </span>
      </div>
      {!isActual && (
        <ProbMiniBar
          home={fixture.home_win_prob}
          draw={fixture.draw_prob}
          away={fixture.away_win_prob}
        />
      )}
    </div>
  );
}
