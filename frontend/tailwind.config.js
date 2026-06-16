/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: '#0a0f1e',
        surface: '#1a1f33',
        surfaceHighlight: '#2a314d',
        primary: '#6366f1',
        primaryHover: '#4f46e5',
        success: '#10b981',
        warning: '#f59e0b',
        danger: '#ef4444',
        textMain: '#f8fafc',
        textMuted: '#94a3b8'
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      }
    },
  },
  plugins: [],
}
