/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  darkMode: 'media',
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#2DD4BF',
          dark: '#0D9488',
        },
        secondary: {
          DEFAULT: '#8B5CF6',
          dark: '#6D28D9',
        },
        surface: {
          DEFAULT: '#F8FAFC',
          dark: '#F1F5F9',
        },
        success: '#22C55E',
        warning: '#F59E0B',
        error: '#EF4444',
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      },
      fontSize: {
        '2xs': '0.625rem',
      },
      spacing: {
        '18': '4.5rem',
      },
      animation: {
        'spin': 'spin 1s linear infinite',
      },
      keyframes: {
        'spin': {
          to: { transform: 'rotate(360deg)' },
        },
      },
      boxShadow: {
        'card': '0 4px 6px -1px rgb(0 0 0 / 0.05), 0 2px 4px -2px rgb(0 0 0 / 0.05)',
        'card-hover': '0 20px 25px -5px rgb(0 0 0 / 0.05), 0 8px 10px -6px rgb(0 0 0 / 0.05)',
        'input-focus': '0 0 0 4px rgba(45, 212, 191, 0.1)',
      },
      borderRadius: {
        'xl': '1rem',
        '2xl': '1.5rem',
      },
      backgroundImage: {
        'gradient-primary': 'linear-gradient(135deg, var(--primary), var(--primary-dark))',
        'gradient-secondary': 'linear-gradient(135deg, var(--secondary), var(--secondary-dark))',
      },
    },
  },
  plugins: [],
} 