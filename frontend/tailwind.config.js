/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        'coral': '#FD3021',
        'coral-light': '#FF6B5B',
        'pink': '#CEB6BD',
        'bg-dark': '#001413',
        'bg-darker': '#000a09',
        'text': '#FBFFFE',
        // Legacy aliases
        'primary': '#FD3021',
        'secondary': '#CEB6BD',
      },
    },
  },
  plugins: [],
}

