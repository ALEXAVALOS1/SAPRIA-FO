/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Definimos el Gris Oxford y el Dorado para usarlos en todo el sitio
        oxford: "#0f172a",
        gold: "#eab308",
      }
    },
  },
  plugins: [],
}