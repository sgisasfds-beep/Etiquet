const API_NGROK = "https://48a2310b9a11.ngrok-free.app";
const API_LOCAL = "http://localhost:4000";

function getApiURL() {
    // Si estás en Render, siempre usa ngrok
    if (window.location.hostname.includes("onrender.com")) {
        return API_NGROK;
    }

    // Si trabajas en local (útil para desarrollo)
    if (window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1") {
        return API_LOCAL;
    }

    // Otros (GitHub Pages, Netlify, etc.)
    return API_NGROK;
}

export const API_URL = getApiURL();
