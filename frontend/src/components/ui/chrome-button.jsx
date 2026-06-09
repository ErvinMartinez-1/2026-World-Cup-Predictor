import { twMerge } from "tailwind-merge";
import LiquidChrome from "@/components/ui/liquid-chrome";


/* Red chrome ramp: dark → mid → bright highlight, all within WC red */
const WC_COLORS = [
  [0.902, 0.114, 0.145],   /* WC red  — dark base   */
  [1.000, 0.294, 0.365],   /* mid red — +0.18 shift */
  [1.000, 0.664, 0.765],   /* bright  — +0.55 shift */
];

export default function ChromeButton({ children, className = "", ...props }) {
  return (
    <button
      className={twMerge(
        "relative py-3 px-5 sm:py-4 sm:px-6 rounded-full border-2 border-[#8B0000] bg-wc-red",
        "overflow-hidden group text-white active:scale-95 transition-all duration-75 shadow-md",
        className
      )}
      {...props}
    >
      {/* Liquid chrome WebGL layer — brightens on hover */}
      <div className="absolute inset-0 z-0 opacity-75 group-hover:opacity-100 transition-opacity duration-500">
        <LiquidChrome
          colors={WC_COLORS}
          speed={2}
          amplitude={0.12}
          interactive={false}
        />
      </div>
      <span className="relative z-10 font-semibold">{children}</span>
    </button>
  );
}
