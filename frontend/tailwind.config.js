/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        sans: ["Aptos", "Segoe UI", "Noto Sans SC", "sans-serif"],
        mono: ["Cascadia Code", "Consolas", "SFMono-Regular", "monospace"],
      },
      colors: {
        ink: "#192026",
        line: "#d7ddd8",
        paper: "#f6f5f0",
        panel: "#fffef9",
        cypress: "#315d50",
        brass: "#9b6a23",
        ember: "#b9472f",
      },
    },
  },
  plugins: [],
};
