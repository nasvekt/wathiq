/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{astro,html,js,jsx,ts,tsx}'],
  theme: {
    extend: {
      colors: {
        primary: '#3ECF8E',
        'primary-dark': '#2BAF74',
        'primary-glow': 'rgba(62, 207, 142, 0.15)',
        surface: '#1C1C1E',
        'surface-light': '#2C2C2E',
        'tech-black': '#0F0F0F',
        charcoal: '#6B7280',
        'white-grey': '#9CA3AF',
      },
      fontFamily: {
        onest: ['Sora', 'system-ui', 'sans-serif'],
        notoSansArabic: ['Noto Sans Arabic', 'sans-serif'],
      },
    },
  },
  plugins: [],
};