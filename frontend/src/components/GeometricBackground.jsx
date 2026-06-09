import { useState, useEffect } from "react";

const RINGS = [
  { insetFrac: 0,      rxFrac: 0,      color: "#2A398D" }, // base fill
  { insetFrac: 0.0267, rxFrac: 0.0178, color: "#E61D25" }, // +24 px on 900 h
  { insetFrac: 0.0533, rxFrac: 0.04,   color: "#3CAC3B" }, // +48 px
  { insetFrac: 0.0844, rxFrac: 0.0578, color: "#2A398D" }, // +76 px
  { insetFrac: 0.1156, rxFrac: 0.0756, color: "#E61D25" }, // +104 px
  { insetFrac: 0.1511, rxFrac: 0.0933, color: "#3CAC3B" }, // +136 px
  { insetFrac: 0.1911, rxFrac: 0.1111, color: "#F7F6F3" }, // +172 px — center
];

export default function GeometricBackground() {
  const [size, setSize] = useState({ w: 1440, h: 900 });

  useEffect(() => {
    const update = () =>
      setSize({
        w: document.documentElement.clientWidth,
        h: document.documentElement.clientHeight,
      });
    update();
    window.addEventListener("resize", update, { passive: true });
    return () => window.removeEventListener("resize", update);
  }, []);

  const { w, h } = size;
  const ref = Math.min(w, h);

  return (
    <div
      className="absolute inset-0 z-0 overflow-hidden"
      aria-hidden="true"
      style={{ pointerEvents: "none" }}
    >
      <svg width={w} height={h} xmlns="http://www.w3.org/2000/svg">
        {RINGS.map(({ insetFrac, rxFrac, color }, i) => {
          const inset = ref * insetFrac;
          const rx    = ref * rxFrac;
          return (
            <rect
              key={i}
              x={inset}
              y={inset}
              width={Math.max(0, w - inset * 2)}
              height={Math.max(0, h - inset * 2)}
              rx={rx}
              fill={color}
            />
          );
        })}
      </svg>
    </div>
  );
}
