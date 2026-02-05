/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    darkMode: 'class',
    theme: {
        extend: {
            colors: {
                // Custom dark theme colors
                'dark': {
                    '50': '#f7f7f8',
                    '100': '#ececf1',
                    '200': '#d9d9e3',
                    '300': '#c5c5d2',
                    '400': '#acacbe',
                    '500': '#8e8ea0',
                    '600': '#6e6e80',
                    '700': '#4a4a5a',
                    '800': '#343541',
                    '900': '#202123',
                    '950': '#0d0d0f',
                },
                'accent': {
                    DEFAULT: '#6366f1',
                    '50': '#eef2ff',
                    '100': '#e0e7ff',
                    '200': '#c7d2fe',
                    '300': '#a5b4fc',
                    '400': '#818cf8',
                    '500': '#6366f1',
                    '600': '#4f46e5',
                    '700': '#4338ca',
                    '800': '#3730a3',
                    '900': '#312e81',
                }
            },
            backdropBlur: {
                xs: '2px',
            },
            animation: {
                'fade-in': 'fadeIn 0.5s ease-out',
                'slide-up': 'slideUp 0.3s ease-out',
                'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
            },
            keyframes: {
                fadeIn: {
                    '0%': { opacity: '0' },
                    '100%': { opacity: '1' },
                },
                slideUp: {
                    '0%': { transform: 'translateY(10px)', opacity: '0' },
                    '100%': { transform: 'translateY(0)', opacity: '1' },
                },
            },
        },
    },
    plugins: [],
}
