import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./lib/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        "t-amber": "#f5c842",
        "t-red": "#ff4444",
        "t-green": "#44ff88",
        "t-bg":  "#0a0a0a",
      },
      fontFamily: {
        terminal: ["VT323", "Courier New", "monospace"],
      },
    },
  },
  plugins: [],
};

export default config;
