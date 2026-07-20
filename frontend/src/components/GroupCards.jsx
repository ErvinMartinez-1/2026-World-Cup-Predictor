import { useState } from "react";
import MatchCard from "./MatchCard";
import { ISO_MAP, flagSrc, displayName } from "../utils/teamData";

const GROUPS = [
  ["Group A", ["Mexico", "South Korea", "South Africa", "Czech Republic"]],
  ["Group B", ["Canada", "Switzerland", "Bosnia and Herzegovina", "Qatar"]],
  ["Group C", ["Brazil", "Morocco", "Haiti", "Scotland"]],
  ["Group D", ["Paraguay", "United States", "Australia", "Turkey"]],
  ["Group E", ["Germany", "Curaçao", "Ivory Coast", "Ecuador"]],
  ["Group F", ["Netherlands", "Japan", "Tunisia", "Sweden"]],
  ["Group G", ["Belgium", "Egypt", "Iran", "New Zealand"]],
  ["Group H", ["Spain", "Cape Verde", "Saudi Arabia", "Uruguay"]],
  ["Group I", ["France", "Senegal", "Norway", "Iraq"]],
  ["Group J", ["Argentina", "Algeria", "Austria", "Jordan"]],
  ["Group K", ["Portugal", "Uzbekistan", "Colombia", "DR Congo"]],
  ["Group L", ["England", "Croatia", "Ghana", "Panama"]],
];

// Real scores come from /api/actual-results (data/results/actual_results.json),
// keyed by the same fixture IDs as /api/fixtures and already oriented to each
// fixture's own home_team/away_team. Returns { home, away } or null if unplayed.
function actualScoreFor(actualData, fixtureId) {
  const m = actualData?.group_stage?.[fixtureId];
  if (!m || m.home_goals == null || m.away_goals == null) return null;
  return { home: m.home_goals, away: m.away_goals };
}

function computeActualStandings(teams, groupFixtures, actualData) {
  const stats = Object.fromEntries(
    teams.map((t) => [
      t,
      { team: t, played: 0, wins: 0, draws: 0, losses: 0, goals_for: 0, goals_against: 0, goal_diff: 0, points: 0 },
    ])
  );

  groupFixtures.forEach((f) => {
    const s = actualScoreFor(actualData, f.id);
    if (!s) return;
    const { home: hg, away: ag } = s;
    const ht = f.home_team;
    const at = f.away_team;
    if (!stats[ht] || !stats[at]) return;
    stats[ht].played++;
    stats[at].played++;
    stats[ht].goals_for += hg;
    stats[ht].goals_against += ag;
    stats[ht].goal_diff += hg - ag;
    stats[at].goals_for += ag;
    stats[at].goals_against += hg;
    stats[at].goal_diff += ag - hg;
    if (hg > ag) {
      stats[ht].wins++; stats[ht].points += 3; stats[at].losses++;
    } else if (ag > hg) {
      stats[at].wins++; stats[at].points += 3; stats[ht].losses++;
    } else {
      stats[ht].draws++; stats[at].draws++; stats[ht].points++; stats[at].points++;
    }
  });

  return Object.values(stats).sort((a, b) =>
    b.points !== a.points ? b.points - a.points :
    b.goal_diff !== a.goal_diff ? b.goal_diff - a.goal_diff :
    b.goals_for - a.goals_for
  );
}

function SingleGroupCard({ groupName, teams, standings, fixtures, actualData, isActual }) {
  const [showMatches, setShowMatches] = useState(false);
  const groupFixtures = fixtures
    .filter((f) => f.group === groupName)
    .sort((a, b) => (a.date < b.date ? -1 : a.date > b.date ? 1 : 0));

  const activeStandings = isActual
    ? computeActualStandings(teams, groupFixtures, actualData)
    : standings;

  const noScoresEntered =
    isActual && !groupFixtures.some((f) => actualScoreFor(actualData, f.id) != null);

  const teamsToRender = activeStandings.length > 0 ? activeStandings.map((s) => s.team) : teams;
  const top2 = new Set(activeStandings.slice(0, 2).map((s) => s.team));

  const cell = (val) => (noScoresEntered ? "—" : val);
  const gdCell = (row) => {
    if (noScoresEntered || !row) return noScoresEntered ? "—" : 0;
    return row.goal_diff > 0 ? `+${row.goal_diff}` : row.goal_diff;
  };

  return (
    <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
      <div className="bg-wc-blue/8 border-b border-wc-blue/20 px-3 sm:px-4 py-2 sm:py-2.5 flex items-center justify-between">
        <h3 className="text-wc-blue font-bold text-xs sm:text-sm tracking-widest uppercase">
          {groupName}
        </h3>
        <span className="text-gray-400 text-[10px] sm:text-xs">{groupFixtures.length} matches</span>
      </div>

      <div className="p-2 sm:p-3">
        <table className="w-full table-fixed text-[10px] sm:text-xs mb-2">
          <colgroup>
            <col className="w-4" />
            <col />
            <col className="w-6" />
            <col className="w-6" />
            <col className="w-6" />
            <col className="w-7" />
            <col className="w-7" />
          </colgroup>
          <thead>
            <tr className="text-gray-400 border-b border-gray-200">
              <th className="text-left pb-1.5 font-normal" />
              <th className="text-left pb-1.5 font-normal">Team</th>
              <th className="text-center pb-1.5 font-normal">W</th>
              <th className="text-center pb-1.5 font-normal">D</th>
              <th className="text-center pb-1.5 font-normal">L</th>
              <th className="text-center pb-1.5 font-normal">GD</th>
              <th className="text-center pb-1.5 font-normal text-gray-500">Pts</th>
            </tr>
          </thead>
          <tbody>
            {teamsToRender.map((team, i) => {
              const row = activeStandings.find((s) => s.team === team);
              const advancing = top2.has(team);
              return (
                <tr key={team} className="border-b border-gray-100 last:border-0">
                  <td className="py-1.5 pr-1">
                    <span className={`text-[9px] font-bold ${advancing ? "text-wc-green" : "text-gray-300"}`}>
                      {i + 1}
                    </span>
                  </td>
                  <td className="py-1.5 overflow-hidden">
                    <div className="flex items-center gap-1.5 min-w-0">
                      <img
                        src={flagSrc(ISO_MAP[team])}
                        alt={team}
                        loading="lazy"
                        style={{
                          width: 18,
                          height: 12,
                          objectFit: "cover",
                          borderRadius: 2,
                          flexShrink: 0,
                          boxShadow: "0 0 0 1px rgba(15,23,42,0.08)",
                        }}
                      />
                      <span
                        title={team}
                        className={`truncate ${advancing ? "font-semibold text-gray-900" : "text-gray-400"}`}
                      >
                        {displayName(team)}
                      </span>
                    </div>
                  </td>
                  <td className="text-center py-1.5 text-gray-600">{cell(row?.wins ?? 0)}</td>
                  <td className="text-center py-1.5 text-gray-600">{cell(row?.draws ?? 0)}</td>
                  <td className="text-center py-1.5 text-gray-600">{cell(row?.losses ?? 0)}</td>
                  <td className="text-center py-1.5 text-gray-600">{gdCell(row)}</td>
                  <td className="text-center py-1.5 font-bold text-gray-700">{cell(row?.points ?? 0)}</td>
                </tr>
              );
            })}
          </tbody>
        </table>

        {noScoresEntered && (
          <p className="text-center text-[10px] text-gray-400 mb-2">
            Results pending
          </p>
        )}

        <button
          onClick={() => setShowMatches((v) => !v)}
          className="w-full text-[11px] text-gray-400 hover:text-wc-blue border border-dashed border-gray-200 hover:border-wc-blue/40 rounded-md py-1 transition-colors duration-150"
        >
          {showMatches ? "Hide matches ▴" : `Show ${groupFixtures.length} matches ▾`}
        </button>

        {showMatches && (
          <div className="mt-2 space-y-1.5">
            {groupFixtures.map((f) => (
              <MatchCard
                key={f.id}
                fixture={f}
                isActual={isActual}
                actualScore={isActual ? actualScoreFor(actualData, f.id) : undefined}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

function GroupCardsSkeleton() {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 xl:grid-cols-4 gap-4 sm:gap-5 items-start">
      {Array.from({ length: 12 }).map((_, i) => (
        <div
          key={i}
          className="rounded-xl border border-gray-200 bg-gray-100 animate-pulse"
          style={{ minHeight: 160 }}
        />
      ))}
    </div>
  );
}

export default function GroupCards({ bracketData, fixturesData, actualData, isActual }) {
  if (!bracketData || !fixturesData) return <GroupCardsSkeleton />;

  const standings = bracketData.group_stage?.standings ?? {};
  const fixtures = fixturesData.fixtures ?? [];

  return (
    <div
      className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 xl:grid-cols-4 gap-4 sm:gap-5 items-start"
      data-testid="group-cards-grid"
    >
      {GROUPS.map(([groupName, teams]) => (
        <SingleGroupCard
          key={groupName}
          groupName={groupName}
          teams={teams}
          standings={standings[groupName] ?? []}
          fixtures={fixtures}
          actualData={actualData}
          isActual={isActual}
        />
      ))}
    </div>
  );
}
