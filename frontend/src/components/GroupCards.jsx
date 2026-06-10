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

// ─── Actual Results ──────────────────────────────────────────────────────────
// Set null → { home: N, away: N } as each match is played.
// IDs match the fixture IDs in fixture_predictions.json exactly.
const ACTUAL_SCORES = {
  // Group A
  "group_a_mexico_vs_south_africa":          null,
  "group_a_mexico_vs_south_korea":           null,
  "group_a_mexico_vs_czech_republic":        null,
  "group_a_south_korea_vs_south_africa":     null,
  "group_a_czech_republic_vs_south_africa":  null,
  "group_a_south_korea_vs_czech_republic":   null,
  // Group B
  "group_b_canada_vs_bosnia_and_herzegovina":     null,
  "group_b_canada_vs_qatar":                      null,
  "group_b_switzerland_vs_canada":                null,
  "group_b_bosnia_and_herzegovina_vs_qatar":      null,
  "group_b_switzerland_vs_bosnia_and_herzegovina": null,
  "group_b_switzerland_vs_qatar":                 null,
  // Group C
  "group_c_brazil_vs_morocco":   null,
  "group_c_brazil_vs_haiti":     null,
  "group_c_brazil_vs_scotland":  null,
  "group_c_morocco_vs_haiti":    null,
  "group_c_morocco_vs_scotland": null,
  "group_c_haiti_vs_scotland":   null,
  // Group D
  "group_d_paraguay_vs_united_states": null,
  "group_d_australia_vs_united_states": null,
  "group_d_turkey_vs_united_states":   null,
  "group_d_paraguay_vs_australia":     null,
  "group_d_turkey_vs_paraguay":        null,
  "group_d_turkey_vs_australia":       null,
  // Group E
  "group_e_germany_vs_curaçao":      null,
  "group_e_germany_vs_ivory_coast":  null,
  "group_e_ecuador_vs_germany":      null,
  "group_e_ivory_coast_vs_curaçao":  null,
  "group_e_ecuador_vs_curaçao":      null,
  "group_e_ecuador_vs_ivory_coast":  null,
  // Group F
  "group_f_netherlands_vs_japan":    null,
  "group_f_netherlands_vs_tunisia":  null,
  "group_f_netherlands_vs_sweden":   null,
  "group_f_japan_vs_tunisia":        null,
  "group_f_japan_vs_sweden":         null,
  "group_f_sweden_vs_tunisia":       null,
  // Group G
  "group_g_belgium_vs_egypt":       null,
  "group_g_belgium_vs_iran":        null,
  "group_g_belgium_vs_new_zealand": null,
  "group_g_iran_vs_egypt":          null,
  "group_g_egypt_vs_new_zealand":   null,
  "group_g_iran_vs_new_zealand":    null,
  // Group H
  "group_h_spain_vs_cape_verde":      null,
  "group_h_spain_vs_saudi_arabia":    null,
  "group_h_spain_vs_uruguay":         null,
  "group_h_saudi_arabia_vs_cape_verde": null,
  "group_h_uruguay_vs_cape_verde":    null,
  "group_h_uruguay_vs_saudi_arabia":  null,
  // Group I
  "group_i_france_vs_senegal": null,
  "group_i_france_vs_norway":  null,
  "group_i_france_vs_iraq":    null,
  "group_i_norway_vs_senegal": null,
  "group_i_senegal_vs_iraq":   null,
  "group_i_norway_vs_iraq":    null,
  // Group J
  "group_j_argentina_vs_algeria": null,
  "group_j_argentina_vs_austria": null,
  "group_j_argentina_vs_jordan":  null,
  "group_j_austria_vs_algeria":   null,
  "group_j_algeria_vs_jordan":    null,
  "group_j_austria_vs_jordan":    null,
  // Group K
  "group_k_portugal_vs_uzbekistan": null,
  "group_k_portugal_vs_colombia":   null,
  "group_k_portugal_vs_dr_congo":   null,
  "group_k_colombia_vs_uzbekistan": null,
  "group_k_uzbekistan_vs_dr_congo": null,
  "group_k_colombia_vs_dr_congo":   null,
  // Group L
  "group_l_england_vs_croatia": null,
  "group_l_england_vs_ghana":   null,
  "group_l_england_vs_panama":  null,
  "group_l_croatia_vs_ghana":   null,
  "group_l_croatia_vs_panama":  null,
  "group_l_panama_vs_ghana":    null,
};
// ─────────────────────────────────────────────────────────────────────────────

function computeActualStandings(teams, groupFixtures) {
  const stats = Object.fromEntries(
    teams.map((t) => [
      t,
      { team: t, played: 0, wins: 0, draws: 0, losses: 0, goals_for: 0, goals_against: 0, goal_diff: 0, points: 0 },
    ])
  );

  groupFixtures.forEach((f) => {
    const s = ACTUAL_SCORES[f.id];
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

function SingleGroupCard({ groupName, teams, standings, fixtures, isActual }) {
  const [showMatches, setShowMatches] = useState(false);
  const groupFixtures = fixtures
    .filter((f) => f.group === groupName)
    .sort((a, b) => (a.date < b.date ? -1 : a.date > b.date ? 1 : 0));

  const activeStandings = isActual
    ? computeActualStandings(teams, groupFixtures)
    : standings;

  const noScoresEntered = isActual && !groupFixtures.some((f) => ACTUAL_SCORES[f.id] != null);

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
                actualScore={isActual ? (ACTUAL_SCORES[f.id] ?? null) : undefined}
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

export default function GroupCards({ bracketData, fixturesData, isActual }) {
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
          isActual={isActual}
        />
      ))}
    </div>
  );
}
