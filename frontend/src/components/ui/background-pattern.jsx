export default function BackgroundPattern() {
  return (
    <>
      {/* Crosshatch art — four angled repeating gradients */}
      <div
        className="absolute inset-0 z-0 pointer-events-none"
        style={{
          backgroundImage: `
            repeating-linear-gradient(22.5deg,  transparent, transparent 2px, rgba(75,  85,  99,  0.06) 2px, rgba(75,  85,  99,  0.06) 3px, transparent 3px, transparent 8px),
            repeating-linear-gradient(67.5deg,  transparent, transparent 2px, rgba(107, 114, 128, 0.05) 2px, rgba(107, 114, 128, 0.05) 3px, transparent 3px, transparent 8px),
            repeating-linear-gradient(112.5deg, transparent, transparent 2px, rgba(55,  65,  81,  0.04) 2px, rgba(55,  65,  81,  0.04) 3px, transparent 3px, transparent 8px),
            repeating-linear-gradient(157.5deg, transparent, transparent 2px, rgba(31,  41,  55,  0.03) 2px, rgba(31,  41,  55,  0.03) 3px, transparent 3px, transparent 8px)
          `,
        }}
      />
      {/* Soft yellow centre glow */}
      <div
        className="absolute inset-0 z-0 pointer-events-none"
        style={{
          backgroundImage: "radial-gradient(circle at center, #FFF991 0%, transparent 70%)",
          opacity: 0.6,
          mixBlendMode: "multiply",
        }}
      />
    </>
  );
}
