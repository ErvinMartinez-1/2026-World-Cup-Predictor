import { useState } from "react";
import { useApiData } from "../hooks/useApiData";
import GroupStageView from "./GroupStageView";
import KnockoutBracket from "./KnockoutBracket";
import TeamProbBar from "./TeamProbBar";

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

export default function PredictionsPage() {
  const [activeTab, setActiveTab] = useState("predicted");
  const [activeView, setActiveView] = useState("knockout");
  const isActual = activeTab === "actual";

  const { data: bracketData,  loading: bracketLoading }  = useApiData("/api/bracket");
  const { data: fixturesData, loading: fixturesLoading } = useApiData("/api/fixtures");
  const { data: mcData }                                  = useApiData("/api/monte-carlo");

  const loading = bracketLoading || fixturesLoading;

  return (
    <div className="min-h-screen bg-[#F7F6F3] pt-16">
      {/* Page header */}
      <div className="bg-[#EDECE9] border-b border-gray-200 px-4 md:px-6 py-4 md:py-5">
        <div className="max-w-7xl mx-auto">
          <h1 className="text-2xl font-bold text-gray-900 mb-1">
            World Cup 2026 · Predictions
          </h1>
          <p className="text-gray-500 text-sm">
            {isActual
              ? "Real match results — updated as the tournament progresses"
              : "Model predictions based on XGBoost + Poisson simulation"}
          </p>
        </div>
      </div>

      {/* Tab bar */}
      <div className="sticky top-16 z-40 bg-[#F7F6F3]/95 backdrop-blur-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 md:px-6 flex flex-wrap items-center justify-between gap-2 py-2 md:py-0">
          <div className="flex gap-2">
            {TABS.map((tab) => {
              const c = COLOR_MAP[tab.color];
              const isActive = activeTab === tab.id;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  data-testid={`tab-${tab.id}`}
                  className={`px-3 py-2 text-xs sm:px-5 sm:py-2.5 sm:text-sm font-semibold rounded-lg border-2 transition-all duration-200 hover:scale-[1.03] hover:shadow-md active:scale-95 ${
                    isActive ? c.active : `bg-transparent ${c.idle}`
                  }`}
                >
                  {tab.label}
                </button>
              );
            })}
          </div>
          <div className="flex gap-2">
            {VIEWS.map((v) => {
              const c = COLOR_MAP[v.color];
              const isActive = activeView === v.id;
              return (
                <button
                  key={v.id}
                  onClick={() => setActiveView(v.id)}
                  className={`px-3 py-1.5 text-xs font-semibold rounded-md border-2 transition-all duration-200 hover:scale-[1.03] hover:shadow-md active:scale-95 ${
                    isActive ? c.active : `bg-transparent ${c.idle}`
                  }`}
                >
                  {v.label}
                </button>
              );
            })}
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 md:px-6 py-8">
        {loading ? (
          <div className="text-center py-20">
            <div className="text-4xl mb-4 animate-spin">⚽</div>
            <p className="text-gray-400">Loading predictions…</p>
          </div>
        ) : (
          <div className="flex flex-col lg:flex-row gap-8">
            {/* Main bracket area */}
            <div className="flex-1 min-w-0">
              {activeView === "group" ? (
                <GroupStageView
                  bracketData={bracketData}
                  fixturesData={fixturesData}
                  isActual={isActual}
                />
              ) : (
                <KnockoutBracket data={bracketData} isActual={isActual} />
              )}
            </div>

            {/* Sidebar: MC probabilities (predicted tab only) */}
            {!isActual && mcData && (
              <div className="lg:w-72 xl:w-80 flex-shrink-0">
                <div className="bg-white rounded-xl border border-gray-200 p-5 sticky top-32 shadow-sm">
                  <h3 className="text-gray-900 font-bold text-sm mb-1">
                    Championship Odds
                  </h3>
                  <p className="text-gray-400 text-xs mb-4">
                    Based on {mcData.n_simulations?.toLocaleString()} simulations
                  </p>
                  <TeamProbBar teams={mcData.teams} limit={12} />
                </div>
              </div>
            )}

            {/* Actual tab note */}
            {isActual && (
              <div className="lg:w-72 xl:w-80 flex-shrink-0">
                <div className="bg-white rounded-xl border border-gray-200 p-5 sticky top-32 text-center shadow-sm">
                  <span className="text-4xl block mb-3">📅</span>
                  <p className="text-gray-900 font-semibold text-sm mb-2">
                    Tournament begins June 11
                  </p>
                  <p className="text-gray-400 text-xs leading-relaxed">
                    Real results will populate as matches are played. Predictions
                    without results show "Not played yet".
                  </p>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
