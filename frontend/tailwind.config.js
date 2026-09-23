/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        nexus: {
          bg: "#0b0f17",
          panel: "#111827",
          border: "#1f2937",
          accent: "#3b82f6",
          danger: "#ef4444",
          warning: "#f59e0b",
          success: "#10b981",
        },
      },
    },
  },
  plugins: [],
};
