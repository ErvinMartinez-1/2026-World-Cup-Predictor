import { Routes, Route } from "react-router-dom";
import NavBar from "./components/NavBar";
import Hero from "./components/Hero";
import ScrollSections from "./components/ScrollSections";
import PredictionsPage from "./components/PredictionsPage";

function LandingPage() {
  return (
    <>
      <Hero />
      <ScrollSections />
      <footer className="bg-[#EDECE9] border-t border-gray-200 py-6 px-4 text-center text-gray-400 text-xs tracking-wide">
        Python · XGBoost · Scikit-learn · Pandas · Playwright · Poisson Regression · Monte Carlo Simulation · React
      </footer>
    </>
  );
}

export default function App() {
  return (
    <>
      <NavBar />
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/predictions" element={<PredictionsPage />} />
      </Routes>
    </>
  );
}
