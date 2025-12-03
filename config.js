// ============================================
//   CONFIGURACIÓN GLOBAL DEL FRONTEND
//   (Compatible con TU server.js actual)
// ============================================

// 1. URL DEL BACKEND EN PRODUCCIÓN
//    👉 Cámbiala por la de tu servidor real
const API_BASE_URL = "https://TU-DOMINIO-O-IP:4000";

// 2. URL DEL BACKEND EN DESARROLLO LOCAL
const API_LOCAL_URL = "http://localhost:4000";

// 3. Detección automática:
//    Si corres desde GitHub Pages, File://, Netlify, etc.
//    usará automáticamente el servidor en producción.
function getApiUrl() {
    const host = window.location.hostname;

    // Ejecutando local (index.html abierto en el navegador)
    if (host === "127.0.0.1" || host === "localhost") {
        return API_LOCAL_URL;
    }

    // Ejecutando en GitHub Pages, Vercel, Netlify, dominio propio, etc.
    return API_BASE_URL;
}

// 4. Exportación para usarlo desde cualquier HTML/JS
export const API_URL = getApiUrl();
