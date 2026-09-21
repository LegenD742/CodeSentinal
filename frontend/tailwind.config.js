/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#16191A",
        paper: "#F6F7F5",
        surface: "#FFFFFF",
        line: "#E2E5E1",
        sentinel: {
          50: "#EEF5F3",
          100: "#D3E5E1",
          300: "#7FAEA5",
          500: "#2F5D5A",
          600: "#264B49",
          700: "#1D3937",
        },
        severity: {
          critical: "#B3261E",
          high: "#C2660E",
          medium: "#B08900",
          low: "#2A5B94",
          info: "#5B6460",
        },
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
        mono: ["'JetBrains Mono'", "ui-monospace", "monospace"],
      },
    },
  },
  plugins: [],
};
