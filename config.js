const API_RENDER = "https://backendet-g5fi.onrender.com";
const API_LOCAL = "http://localhost:4000";

function getApiURL() {
    const host = window.location.hostname;

    if (host === "localhost" || host === "127.0.0.1") {
        return API_LOCAL;
    }

    return API_RENDER;
}

export const API_URL = getApiURL();
