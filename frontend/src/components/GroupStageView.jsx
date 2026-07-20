import GroupCards from "./GroupCards";

export default function GroupStageView({ bracketData, fixturesData, actualData, isActual }) {
  return (
    <GroupCards
      bracketData={bracketData}
      fixturesData={fixturesData}
      actualData={actualData}
      isActual={isActual}
    />
  );
}
