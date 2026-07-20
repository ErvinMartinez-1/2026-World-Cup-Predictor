import { useState } from "react";
import { useApiData } from "../hooks/useApiData";
import GroupStageView from "./GroupStageView";
import KnockoutBracket from "./KnockoutBracket";
import TeamProbBar from "./TeamProbBar";
import BackgroundPattern from "./ui/background-pattern";
import { AnimatedBorderButton } from "./ui/AnimatedBorderButton";

const TABS = [
  { id: "predicted", label: "Predicted Bracket", color: "blue" },
  { id: "actual",    label: "Actual Results",    color: "red"  },
];

const VIEWS = [
  { id: "group",    label: "Group Stage", color: "green" },
  { id: "knockout", label: "Knockout",    color: "dark"  },
];

const COLOR_MAP = {
  blue: {
    active: "bg-wc-blue  border-wc-blue  text-white shadow-sm",
    idle:   "border-wc-blue/40  text-wc-blue  hover:bg-wc-blue  hover:border-wc-blue  hover:text-white",
  },
  red: {
    active: "bg-wc-red   border-wc-red   text-white shadow-sm",
    idle:   "border-wc-red/40   text-wc-red   hover:bg-wc-red   hover:border-wc-red   hover:text-white",
  },
  green: {
    active: "bg-wc-green border-wc-green text-white shadow-sm",
    idle:   "border-wc-green/40 text-wc-green hover:bg-wc-green hover:border-wc-green hover:text-white",
  },
  dark: {
    active: "bg-wc-dark  border-wc-dark  text-white shadow-sm",
    idle:   "border-wc-dark/40  text-wc-dark  hover:bg-wc-dark  hover:border-wc-dark  hover:text-white",
  },
};

// Hex values matching the wc-* Tailwind colors for the animated glow
const GLOW_HEX = {
  blue:  "#2A398D",
  red:   "#E61D25",
  green: "#3CAC3B",
  dark:  "#474A4A",
};

export default function PredictionsPage() {
  const [activeTab, setActiveTab] = useState("predicted");
  const [activeView, setActiveView] = useState("knockout");
  const isActual = activeTab === "actual";

  const { data: bracketData,  loading: bracketLoading }  = useApiData("/api/bracket");
  const { data: fixturesData, loading: fixturesLoading } = useApiData("/api/fixtures");
  const { data: mcData }                                  = useApiData("/api/monte-carlo");
  const { data: actualData }                              = useApiData("/api/actual-results");

  const loading = bracketLoading || fixturesLoading;

  return (
    <div className="relative min-h-screen bg-[#F7F6F3] pt-16">
      <BackgroundPattern />
      <div className="relative z-10">
      {/* Tab bar — title sits above the left tab buttons */}
      <div className="sticky top-16 z-40 bg-[#F7F6F3]/95 backdrop-blur-sm border-b border-gray-200">
        <div className="w-full px-4 md:px-6 flex flex-wrap items-end justify-between gap-3 py-3">

          {/* Left: title + subtitle + tab buttons stacked */}
          <div className="flex flex-col gap-2">
            <div>
              <h1 className="text-xl font-bold text-gray-900 leading-tight">
                World Cup 2026 · Predictions
              </h1>
              <p className="text-gray-500 text-xs mt-0.5">
                {isActual
                  ? "Real match results — updated as the tournament progresses"
                  : "Model predictions based on XGBoost + Poisson simulation"}
              </p>
            </div>
            <div className="flex gap-2">
              {TABS.map((tab) => {
                const c = COLOR_MAP[tab.color];
                const isActive = activeTab === tab.id;
                return (
                  <AnimatedBorderButton
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    data-testid={`tab-${tab.id}`}
                    glowColor={isActive ? "#ffffff" : GLOW_HEX[tab.color]}
                    duration={4}
                    className={`px-3 py-1.5 text-xs font-semibold rounded-md border-2 transition-all duration-200 hover:scale-[1.03] hover:shadow-md active:scale-95 ${
                      isActive ? c.active : `bg-transparent ${c.idle}`
                    }`}
                  >
                    {tab.label}
                  </AnimatedBorderButton>
                );
              })}
            </div>
          </div>

          {/* Right: view toggle buttons */}
          <div className="flex gap-2">
            {VIEWS.map((v) => {
              const c = COLOR_MAP[v.color];
              const isActive = activeView === v.id;
              return (
                <AnimatedBorderButton
                  key={v.id}
                  onClick={() => setActiveView(v.id)}
                  glowColor={isActive ? "#ffffff" : GLOW_HEX[v.color]}
                  duration={4}
                  className={`px-3 py-1.5 text-xs font-semibold rounded-md border-2 transition-all duration-200 hover:scale-[1.03] hover:shadow-md active:scale-95 ${
                    isActive ? c.active : `bg-transparent ${c.idle}`
                  }`}
                >
                  {v.label}
                </AnimatedBorderButton>
              );
            })}
          </div>

        </div>
      </div>

      {/* Content */}
      <div className="w-full px-4 md:px-6 py-8">
        {loading ? (
          <div className="text-center py-20">
            <div className="text-4xl mb-4 animate-spin">⚽</div>
            <p className="text-gray-400">Loading predictions…</p>
          </div>
        ) : (
          <div className="flex flex-col lg:flex-row gap-20">
            {/* Main bracket area */}
            <div className="flex-1 min-w-0">
              {activeView === "group" ? (
                <GroupStageView
                  bracketData={bracketData}
                  fixturesData={fixturesData}
                  actualData={actualData}
                  isActual={isActual}
                />
              ) : (
                <KnockoutBracket data={bracketData} actualData={actualData} isActual={isActual} />
              )}
            </div>

            {/* Sidebar: MC probabilities (knockout + predicted tab only) */}
            {activeView === "knockout" && !isActual && mcData && (
              <div className="lg:w-[440px] xl:w-[520px] flex-shrink-0">
                <div className="bg-white rounded-xl border border-gray-200 p-5 sticky top-32 shadow-sm">
                  <h3 className="text-gray-900 font-bold text-sm mb-1">
                    Championship Odds
                  </h3>
                  <p className="text-gray-400 text-xs mb-4">
                    Based on {mcData.n_simulations?.toLocaleString()} simulations
                  </p>
                  <TeamProbBar teams={mcData.teams} />
                </div>
              </div>
            )}

          </div>
        )}
      </div>
      </div>{/* end relative z-10 */}
    </div>
  );
}
