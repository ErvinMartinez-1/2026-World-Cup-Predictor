/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        sans:    ['"Poppins"', 'system-ui', 'sans-serif'],
        display: ['"TASA Orbiter"', '"Poppins"', 'sans-serif'],
        akt:     ['"Akt"', '"Poppins"', 'sans-serif'],
      },
      colors: {
        wc: {
          green: "#3CAC3B",
          blue:  "#2A398D",
          red:   "#E61D25",
          gray:  "#D1D4D1",
          dark:  "#474A4A",
        },
      },
      animation: {
        float:      "float 4s ease-in-out infinite",
        "fade-up":  "fadeUp 0.6s ease forwards",
        spotlight:  "spotlight 2s ease .75s 1 forwards",
      },
      keyframes: {
        float: {
          "0%, 100%": { transform: "translateY(0px)" },
          "50%":      { transform: "translateY(-14px)" },
        },
        fadeUp: {
          from: { opacity: "0", transform: "translateY(32px)" },
          to:   { opacity: "1", transform: "translateY(0)" },
        },
        spotlight: {
          "0%":   { opacity: "0", transform: "translate(-72%, -62%) scale(0.5)" },
          "100%": { opacity: "1", transform: "translate(-50%, -40%) scale(1)" },
        },
      },
    },
  },
  plugins: [],
};
