// URL del backend expuesto con ngrok
const API_NGROK = "https://234c-186-180-6-146.ngrok-free.app";

const API_LOCAL = "http://localhost:4000";

function getApiURL() {
    const host = window.location.hostname;


    if (host.includes("onrender.com")) {
        return API_NGROK;
    }

    if (host === "localhost" || host === "127.0.0.1") {
        return API_LOCAL;
    }

    return API_NGROK;
}

export const API_URL = getApiURL();
