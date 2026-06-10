import GroupCards from "./GroupCards";

export default function GroupStageView({ bracketData, fixturesData, isActual }) {
  return (
    <GroupCards
      bracketData={bracketData}
      fixturesData={fixturesData}
      isActual={isActual}
    />
  );
}
