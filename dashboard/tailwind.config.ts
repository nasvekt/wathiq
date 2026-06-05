import type { Config } from 'tailwindcss';

export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        // Primary brand
        primary: {
          DEFAULT: '#3ECF8E',
          dark: '#2BAF74',
          glow: 'rgba(62, 207, 142, 0.15)',
          50: '#E8FBF2',
          100: '#C5F5DF',
          200: '#9EEDCA',
          300: '#6EE4B1',
          400: '#3ECF8E',
          500: '#2BAF74',
          600: '#1F8F5E',
          700: '#18704A',
          800: '#135438',
          900: '#0E3A27',
        },
        // Background surfaces
        surface: {
          base: '#0F0F0F',
          card: '#1C1C1E',
          sidebar: '#111111',
          content: '#F8F9FA',
          'content-card': '#FFFFFF',
          'content-hover': '#F0F1F3',
        },
        // Status colors
        status: {
          ready: '#3ECF8E',
          review: '#F5A623',
          blocked: '#E53E3E',
          'at-risk': '#F97316',
          pending: '#94A3B8',
        },
        // Nitaqat band colors
        band: {
          platinum: '#E8D5B7',
          'high-green': '#22C55E',
          'low-green': '#86EFAC',
          yellow: '#EAB308',
          red: '#DC2626',
        },
      },
      fontFamily: {
        sora: ['Sora', 'system-ui', 'sans-serif'],
        dm: ['DM Mono', 'monospace'],
        arabic: ['Noto Sans Arabic', 'sans-serif'],
      },
      borderRadius: {
        xl: '0.75rem',
        '2xl': '1rem',
      },
      boxShadow: {
        'card': '0 1px 3px rgba(0, 0, 0, 0.06), 0 1px 2px rgba(0, 0, 0, 0.04)',
        'card-hover': '0 4px 12px rgba(0, 0, 0, 0.08), 0 2px 4px rgba(0, 0, 0, 0.04)',
        'glow-primary': '0 0 20px rgba(62, 207, 142, 0.3)',
        'sidebar': '2px 0 8px rgba(0, 0, 0, 0.1)',
      },
      animation: {
        'pulse-glow': 'pulse-glow 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'slide-in': 'slide-in 0.3s ease-out',
      },
      keyframes: {
        'pulse-glow': {
          '0%, 100%': { boxShadow: '0 0 8px rgba(62, 207, 142, 0.2)' },
          '50%': { boxShadow: '0 0 24px rgba(62, 207, 142, 0.5)' },
        },
        'slide-in': {
          '0%': { opacity: '0', transform: 'translateX(-10px)' },
          '100%': { opacity: '1', transform: 'translateX(0)' },
        },
      },
    },
  },
  plugins: [],
} satisfies Config;
