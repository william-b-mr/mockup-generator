/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,jsx}",
  ],
  theme: {
    extend: {
      colors: {
        'mbc-red': '#e31e24',
        'mbc-dark-red': '#b81419',
      },
    },
  },
  plugins: [],
}

