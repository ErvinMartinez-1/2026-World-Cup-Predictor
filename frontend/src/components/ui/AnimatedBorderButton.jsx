import { motion } from "framer-motion";
import { cn } from "../../lib/utils";

/**
 * Button with an animated glowing dot that travels around the border.
 *
 * Props:
 *  - glowColor  : hex color of the traveling glow (e.g. "#2A398D")
 *  - duration   : seconds for one full loop (default 4)
 *  - className  : passed straight to the <button>
 *  - All other props forwarded to <button>
 */
export function AnimatedBorderButton({
  children,
  className,
  glowColor = "#ffffff",
  duration = 4,
  ...props
}) {
  return (
    <button className={cn("relative", className)} {...props}>
      {/* Animated border overlay — uses CSS Motion Path to travel the perimeter */}
      <div
        className={cn(
          "absolute -inset-px pointer-events-none rounded-[inherit] border-2 border-transparent",
          "[mask-clip:padding-box,border-box]",
          "[mask-composite:intersect]",
          "[mask-image:linear-gradient(transparent,transparent),linear-gradient(#000,#000)]"
        )}
      >
        <motion.div
          className="absolute aspect-square"
          style={{
            width: 22,
            offsetPath: "rect(0 auto auto 0 round 8px)",
            background: `linear-gradient(to right, transparent, ${glowColor}, ${glowColor})`,
          }}
          animate={{ offsetDistance: ["0%", "100%"] }}
          transition={{ repeat: Infinity, duration, ease: "linear" }}
        />
      </div>
      {children}
    </button>
  );
}
