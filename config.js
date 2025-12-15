// URL del backend expuesto con ngrok
const API_NGROK = "https://e878d1359120.ngrok-free.app";

// URL del backend local (solo para desarrollo en tu PC)
const API_LOCAL = "http://localhost:4000";

function getApiURL() {
    const host = window.location.hostname;

    // ⭐ Si estás en Render → usar siempre ngrok
    if (host.includes("onrender.com")) {
        return API_NGROK;
    }

    // ⭐ Si estás ejecutando el HTML directamente en tu PC
    if (host === "localhost" || host === "127.0.0.1") {
        return API_LOCAL;
    }

    // ⭐ GitHub Pages, Netlify, dominio propio → usar ngrok
    return API_NGROK;
}

export const API_URL = getApiURL();
