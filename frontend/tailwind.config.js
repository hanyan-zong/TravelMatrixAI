/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      fontFamily: {
        sans: ['-apple-system', 'BlinkMacSystemFont', '"Microsoft YaHei"', '"PingFang SC"', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
