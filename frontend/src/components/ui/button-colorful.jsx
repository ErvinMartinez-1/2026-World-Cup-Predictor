import { clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'

function cn(...inputs) { return twMerge(clsx(inputs)) }

/* WC palette: blue → green → red → silver — dark used as button shell */
const WC_GRADIENT =
  'linear-gradient(to right, #2A398D, #3CAC3B, #E61D25, #D1D4D1)'

export default function ButtonColorful({ className, children = 'Explore', ...props }) {
  return (
    <button
      className={cn(
        'group relative overflow-hidden rounded-full px-6 py-4',
        'text-sm font-semibold tracking-wide text-white',
        'bg-wc-dark shadow-md',
        'transition-all duration-200 active:scale-95',
        className
      )}
      {...props}
    >
      {/* Blurred gradient layer — softens into a luminous glow, brightens on hover */}
      <div
        className="absolute inset-0 opacity-80 blur transition-opacity duration-500 group-hover:opacity-100"
        style={{ background: WC_GRADIENT }}
      />

      <div className="relative flex items-center justify-center gap-2">
        {children}
      </div>
    </button>
  )
}
