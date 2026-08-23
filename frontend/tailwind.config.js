/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        church: {
          950: "#090B10",
          900: "#0F141C",
          850: "#161D28",
          800: "#1E2736",
          700: "#2B374A",
          600: "#3E4E68",
          accent: "#3B82F6",
          gold: "#F59E0B",
          glow: "#60A5FA",
        }
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
        mono: ["JetBrains Mono", "monospace"]
      }
    },
  },
  plugins: [],
};
