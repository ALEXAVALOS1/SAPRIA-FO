import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  // Esto es VITAL para que no salga pantalla blanca en localhost ni en GitHub
  base: '/URBIPREX/', 
})