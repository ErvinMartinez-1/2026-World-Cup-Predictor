import { useNavigate } from "react-router-dom";
import { useEffect, useRef } from "react";
import { SplineScene } from "./ui/splite";
import GeometricBackground from "./GeometricBackground";
import ChromeButton from "./ui/chrome-button";

export default function Hero() {
  const navigate = useNavigate();
  const splineContainerRef = useRef(null);

  const handleSplineLoad = () => {
    const canvas = splineContainerRef.current?.querySelector("canvas");
    if (canvas) canvas.style.background = "transparent";
  };

  useEffect(() => {
    const el = splineContainerRef.current;
    if (!el) return;
    const onWheel = (e) => window.scrollBy({ top: e.deltaY, behavior: "auto" });
    el.addEventListener("wheel", onWheel, { passive: true });
    return () => el.removeEventListener("wheel", onWheel);
  }, []);

  return (
    <section
      className="relative h-screen flex items-center overflow-hidden"
      data-testid="hero-section"
    >
      <GeometricBackground />

      <div className="relative z-10 flex flex-col md:flex-row h-full w-full">
        {/* Card — stacks on top for mobile, left column on desktop */}
        <div
          className="flex-1 flex flex-col justify-center pt-[20vmin] pb-3 pr-[20vmin] md:pt-0 md:pb-0 md:pr-6"
          style={{ paddingLeft: "clamp(1rem, 20vmin, 19rem)" }}
        >
          <div
            className="bg-white/90 backdrop-blur-md rounded-2xl px-5 py-3 sm:p-8 max-w-lg"
            style={{ boxShadow: "0 8px 24px rgba(0,0,0,0.08)" }}
          >
            <h1 className="text-2xl sm:text-4xl md:text-5xl font-bold leading-tight tracking-tight text-gray-900">
              World Cup{" "}
              <span className="text-wc-red">2026</span>
              <br />
              Match Predictor
            </h1>
            <span className="inline-block text-m font-bold tracking-widest uppercase text-wc-red mb-2 sm:mb-4">
              Using Machine Learning
            </span>

            <p className="mt-1 sm:mt-3 text-sm text-gray-500 leading-relaxed">
              Trained on 5,000+ international matches, predicting every
              World Cup fixture from group stage to the final.
            </p>

            <div className="mt-3 sm:mt-6 flex justify-center">
              <ChromeButton onClick={() => navigate("/predictions")}>
                Explore Predictions
              </ChromeButton>
            </div>
          </div>
        </div>

        {/* Spline — fills bottom half on mobile, right column on desktop */}
        <div
          ref={splineContainerRef}
          className="flex-1 relative md:flex-[1.4] pt-[5vmin] md:pt-[20vmin]"
          style={{ paddingBottom: "2vmin" }}
        >
          <SplineScene
            scene="https://prod.spline.design/d8hZij2YKDRp1cou/scene.splinecode"
            className="w-full h-full"
            onLoad={handleSplineLoad}
          />
        </div>
      </div>
    </section>
  );
}
