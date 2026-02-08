/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      },
      colors: {
        'deep-black': '#000000',
        'dark-gray': '#0b0b0b',
        'burnt-orange': '#ea580c',
        'copper': '#b45309',
        'amber-bright': '#fcd34d',
        'white-bone': '#f9fafb',
        'lava-red': '#ef4444',
        'emerald-green': '#10b981',
        'orange-alert': '#f97316',
      },
      boxShadow: {
        'glow': '0 0 30px -10px rgba(234, 88, 12, 0.3)',
      }
    },
  },
  plugins: [],
};