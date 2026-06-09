import MatchCard from "./MatchCard";

const GROUP_KEYS = [
  "Group A","Group B","Group C","Group D",
  "Group E","Group F","Group G","Group H",
  "Group I","Group J","Group K","Group L",
];

function StandingsTable({ standings }) {
  if (!standings || standings.length === 0) return null;
  return (
    <table className="w-full text-xs mb-3">
      <thead>
        <tr className="text-gray-400 border-b border-gray-200">
          <th className="text-left py-1 font-normal">Team</th>
          <th className="text-center py-1 font-normal">W</th>
          <th className="text-center py-1 font-normal">D</th>
          <th className="text-center py-1 font-normal">L</th>
          <th className="text-center py-1 font-normal">GD</th>
          <th className="text-center py-1 font-normal text-wc-gray/70">Pts</th>
        </tr>
      </thead>
      <tbody>
        {standings.map((row, i) => (
          <tr
            key={row.team}
            className={`border-b border-gray-100 last:border-0 ${
              i < 2 ? "text-gray-900" : "text-gray-400"
            }`}
          >
            <td className="py-1 truncate max-w-[80px]">
              <span
                className={`inline-block w-4 text-center text-[10px] mr-1 ${
                  i < 2 ? "text-wc-green" : "text-wc-dark"
                }`}
              >
                {i + 1}
              </span>
              {row.team}
            </td>
            <td className="text-center py-1">{row.wins}</td>
            <td className="text-center py-1">{row.draws}</td>
            <td className="text-center py-1">{row.losses}</td>
            <td className="text-center py-1">
              {row.goal_diff > 0 ? `+${row.goal_diff}` : row.goal_diff}
            </td>
            <td className="text-center py-1 font-bold text-gray-700">{row.points}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

function GroupCard({ groupName, standings, fixtures, isActual }) {
  const groupFixtures = fixtures.filter((f) => f.group === groupName);

  return (
    <div className="bg-white rounded-xl border border-gray-200 overflow-hidden shadow-sm">
      <div className="bg-wc-blue/8 border-b border-wc-blue/20 px-4 py-2.5 flex items-center justify-between">
        <span className="text-wc-blue font-bold text-sm tracking-wide">{groupName}</span>
        <span className="text-gray-400 text-xs">{groupFixtures.length} matches</span>
      </div>
      <div className="p-3">
        <StandingsTable standings={standings} />
        <div className="space-y-1.5">
          {groupFixtures.map((fixture) => (
            <MatchCard key={fixture.id} fixture={fixture} isActual={isActual} />
          ))}
        </div>
      </div>
    </div>
  );
}

export default function GroupStageView({ bracketData, fixturesData, isActual }) {
  if (!bracketData || !fixturesData) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {GROUP_KEYS.map((g) => (
          <div key={g} className="h-72 bg-gray-100 rounded-xl border border-gray-200 animate-pulse" />
        ))}
      </div>
    );
  }

  const standings = bracketData.group_stage?.standings ?? {};
  const fixtures = fixturesData.fixtures ?? [];

  return (
    <div
      className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4"
      data-testid="group-stage-grid"
    >
      {GROUP_KEYS.map((g) => (
        <GroupCard
          key={g}
          groupName={g}
          standings={standings[g] ?? []}
          fixtures={fixtures}
          isActual={isActual}
        />
      ))}
    </div>
  );
}
