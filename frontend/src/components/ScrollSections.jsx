import { useRef, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import ChromeButton from "@/components/ui/chrome-button";
import BackgroundPattern from "@/components/ui/background-pattern";

function useVisible(threshold = 0.1) {
  const ref = useRef(null);
  const [visible, setVisible] = useState(false);
  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const observer = new IntersectionObserver(
      ([entry]) => { if (entry.isIntersecting) setVisible(true); },
      { threshold, rootMargin: "0px 0px -18% 0px" }
    );
    observer.observe(el);
    return () => observer.disconnect();
  }, [threshold]);
  return [ref, visible];
}

function Section({ children, className = "" }) {
  const [ref, visible] = useVisible();
  return (
    <section
      ref={ref}
      className={`relative py-10 px-4 sm:py-20 sm:px-6 transition-opacity duration-500 ${
        visible ? "opacity-100" : "opacity-0"
      } ${className}`}
    >
      <div className="relative z-10 max-w-5xl mx-auto">{children}</div>
    </section>
  );
}

function SectionTag({ label }) {
  return (
    <span className="inline-block text-xs font-bold tracking-widest uppercase text-wc-green mb-4 border border-wc-green/30 px-3 py-1 rounded-full">
      {label}
    </span>
  );
}

// ─── Key Stats ────────────────────────────────────────────────────────────────

const STATS = [
  { value: "5,221",  label: "international matches analyzed",            color: "text-wc-blue" },
  { value: "48",     label: "World Cup 2026 teams simulated",            color: "text-wc-green" },
  { value: "10,000", label: "Monte Carlo tournament simulations",        color: "text-wc-red" },
  { value: "59.1%",  label: "model validation accuracy",                 color: "text-wc-blue" },
  { value: "0.176",  label: "Ranked Probability Score (lower is better)", color: "text-wc-green" },
  { value: "4 yrs",  label: "of international football data (2021–2026)", color: "text-wc-red" },
];

function StatsBar() {
  return (
    <Section dark>
      <h2 className="text-2xl md:text-3xl font-bold text-gray-900 mb-8">
        Built on Real Data, Validated on Real Results
      </h2>
      <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
        {STATS.map(({ value, label, color }) => (
          <div
            key={label}
            className="bg-white rounded-xl p-5 border border-gray-200 shadow-sm"
          >
            <div className={`text-3xl md:text-4xl font-bold ${color}`}>{value}</div>
            <div className="text-xs text-gray-500 mt-1 leading-snug">{label}</div>
          </div>
        ))}
      </div>
    </Section>
  );
}

// ─── How It Works ─────────────────────────────────────────────────────────────

const STEPS = [
  {
    number: "01",
    title: "Data Collection",
    color: "border-wc-blue/40",
    accent: "text-wc-blue",
    body: "Three independent data sources are combined: International match results dating back to 2021, Live FIFA Men's Football (Soccer) world rankings scraped directly from FIFA's website, and ELO ratings covering 244 nations. All source were cleaned, normalised, and unified into a single pipeline.",
  },
  {
    number: "02",
    title: "Feature Engineering",
    color: "border-wc-green/40",
    accent: "text-wc-green",
    body: "60 predictive features are built for every fixture: Includes team ELO ratings, the specific teams recent form across the last 10 matches weighted by tournament importance, head-to-head records, goal scoring and conceding averages, and host nation advantage by city.",
  },
  {
    number: "03",
    title: "Machine Learning Model",
    color: "border-wc-red/40",
    accent: "text-wc-red",
    body: "An XGBoost classifier predicts match outcomes with win, draw, and loss probabilities. A Poisson regression model independently predicts the scoreline for each team. Both models are trained on historical data and validated on a time based split to prevent data leakage.",
  },
  {
    number: "04",
    title: "Tournament Simulation",
    color: "border-wc-blue/40",
    accent: "text-wc-blue",
    body: "The full 2026 bracket is simulated. All 48 group stage matches, including Group Stages, Round of 32, Round of 16, Quarter Finals, Semi Finals, and the Final. In knockout rounds, draw probabilities are redistributed proportionally and penalty shootouts are simulated when teams are within 5% of each other.",
  },
];

function HowItWorks() {
  return (
    <Section>
      <h2 className="text-2xl md:text-3xl font-bold text-gray-900 mb-8">
        How It Works
      </h2>
      <div className="grid md:grid-cols-2 gap-5">
        {STEPS.map(({ number, title, color, accent, body }) => (
          <div
            key={number}
            className={`bg-white rounded-xl p-6 border ${color} shadow-sm`}
          >
            <div className={`text-4xl font-black ${accent} opacity-20 leading-none mb-3`}>
              {number}
            </div>
            <h3 className={`font-bold text-base mb-3 ${accent}`}>{title}</h3>
            <p className="text-gray-500 leading-relaxed">{body}</p>
          </div>
        ))}
      </div>
    </Section>
  );
}

// ─── Model Transparency ───────────────────────────────────────────────────────

function ModelTransparency() {
  return (
    <Section dark>
      <div className="bg-white rounded-xl border border-wc-green/30 p-8 shadow-sm">
        <h2 className="text-2xl md:text-3xl font-bold text-gray-900 mb-4">
          Why Trust This Model?
        </h2>
        <p className="text-gray-500 leading-relaxed">
          Most football predictions are black boxes. Every prediction here comes
          with full probability breakdowns not just a winner, but the percentage
          chance of each outcome. The model was validated on matches it had never
          seen, achieving a{" "}
          <span className="font-semibold text-wc-green">
            Ranked Probability Score of 0.176
          </span>{" "}
          compared to{" "}
          <span className="font-semibold text-gray-700">
            0.333 for a random prediction
          </span>
          . It correctly accounts for neutral venues, host nation advantage, and
          tournament stage, factors most simple models ignore.
        </p>
      </div>
    </Section>
  );
}

// ─── Info Cards ───────────────────────────────────────────────────────────────

const DATA_ROWS = [
  { label: "Match results",      value: "International fixtures 2021–2026 (5,221 matches)" },
  { label: "FIFA Rankings",      value: "Official rankings scraped from inside.fifa.com" },
  { label: "ELO Ratings",        value: "World Football ELO ratings (eloratings.net)" },
  { label: "Training period",    value: "January 2021 – December 2024" },
  { label: "Validation period",  value: "January 2025 – December 2025" },
  { label: "Prediction target",  value: "June 2026 World Cup fixtures" },
];

const LIMITATIONS = [
  "No player-level data — injuries, suspensions, and squad changes are not accounted for.",
  "FIFA rankings update monthly so very recent form shifts may not be fully captured.",
  "Football contains genuine randomness that no model can eliminate — upsets will happen.",
  "Treat probabilities as informed estimates, not certainties.",
];

function InfoCards() {
  return (
    <Section>
      <div className="grid md:grid-cols-2 gap-6">

        {/* Monte Carlo */}
        <div className="bg-white rounded-xl border border-wc-blue/30 p-6 shadow-sm md:col-span-2">
          <h2 className="text-2xl md:text-3xl font-bold text-gray-900 mb-4">
            What is Monte Carlo Simulation?
          </h2>
          <p className="text-gray-500 leading-relaxed">
            Rather than predicting one fixed outcome, the tournament is simulated{" "}
            <span className="font-semibold text-gray-700">10,000 times</span>. Each
            simulation samples from match probabilities — meaning upsets happen, just
            at their correct frequency. The result is not{" "}
            <em>"Spain wins the World Cup"</em> but{" "}
            <em className="text-wc-blue not-italic font-semibold">
              "Spain has a 24.5% chance of winning the World Cup."
            </em>{" "}
            This is how professional forecasters and betting markets think about
            tournament predictions.
          </p>
        </div>

        {/* Data sources */}
        <div className="bg-white rounded-xl border border-wc-green/30 p-6 shadow-sm">
          <h2 className="text-2xl md:text-3xl font-bold text-gray-900 mb-4">
            What Data Powers This?
          </h2>
          <p className="space-y-2">
            {DATA_ROWS.map(({ label, value }) => (
              <div key={label} className="flex flex-col sm:flex-row sm:gap-3">
                <dt className="text-sm font-semibold text-wc-green shrink-0 w-36">{label}</dt>
                <dd className="text-sm text-gray-500">{value}</dd>
              </div>
            ))}
          </p>
        </div>

        {/* Limitations */}
        <div className="bg-white rounded-xl border border-wc-red/30 p-6 shadow-sm">
          <h2 className="text-2xl md:text-3xl font-bold text-gray-900 mb-4">
            What This Model Can&apos;t Do
          </h2>
          <ul className="space-y-2">
            {LIMITATIONS.map((item, i) => (
              <li key={i} className="flex gap-2 text-sm text-gray-500 leading-relaxed">
                <span className="text-wc-red shrink-0 mt-0.5">×</span>
                {item}
              </li>
            ))}
          </ul>
        </div>

      </div>
    </Section>
  );
}

// ─── CTA ──────────────────────────────────────────────────────────────────────

function CtaSection() {
  const navigate = useNavigate();
  return (
    <Section dark>
      <div className="text-center py-6">
        <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
          Explore Every Prediction
        </h2>
        <p className="text-gray-500 mb-8 max-w-md mx-auto text-sm leading-relaxed">
          View the full predicted bracket from group stage to the final,
          and compare with real results as the tournament progresses.
        </p>
        <ChromeButton onClick={() => navigate("/predictions")}>
          View Predictions →
        </ChromeButton>
      </div>
    </Section>
  );
}

// ─── Root ─────────────────────────────────────────────────────────────────────

export default function ScrollSections() {
  return (
    <div className="relative bg-[#F7F6F3]">
      <BackgroundPattern />
      <StatsBar />
      <HowItWorks />
      <ModelTransparency />
      <InfoCards />
      <CtaSection />
    </div>
  );
}
