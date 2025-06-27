// static/js/global.js

// --- Constants ---
const API_BASE_URL = '/api/v1'; // Adjust if your URL structure is different
const ACCESS_TOKEN_LIFETIME_MINUTES = 15; // Should match your Django settings

// --- Utility Functions ---

/**
 * Decodes the payload of a JWT token without verifying the signature.
 * This is safe to use on the client-side to check expiry dates.
 * @param {string} token - The JWT access token.
 * @returns {object|null} The decoded payload or null if invalid.
 */
const decodeJwt = (token) => {
    try {
        const base64Url = token.split('.')[1];
        const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
        const jsonPayload = decodeURIComponent(atob(base64).split('').map(function(c) {
            return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
        }).join(''));
        return JSON.parse(jsonPayload);
    } catch (e) {
        console.error("Failed to decode JWT:", e);
        return null;
    }
};

/**
 * Retrieves user data and tokens from localStorage.
 * @returns {{accessToken: string|null, refreshToken: string|null, user: object|null}}
 */
const getAuthData = () => {
    try {
        const user = JSON.parse(localStorage.getItem('userData'));
        const accessToken = localStorage.getItem('accessToken');
        const refreshToken = localStorage.getItem('refreshToken');
        return { user, accessToken, refreshToken };
    } catch (e) {
        return { user: null, accessToken: null, refreshToken: null };
    }
};

/**
 * Clears all authentication data from localStorage.
 */
const clearAuthData = () => {
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    localStorage.removeItem('userData');
};

// --- Core Authentication Logic ---

/**
 * Silently refreshes the access token using the refresh token.
 * @returns {string|null} The new access token or null if refresh fails.
 */
const refreshAccessToken = async () => {
    const { refreshToken } = getAuthData();
    if (!refreshToken) {
        console.log("No refresh token available.");
        logoutUser();
        return null;
    }

    try {
        // NOTE: A dedicated refresh endpoint is needed in your urls.py for Simple JWT
        const response = await fetch(`${API_BASE_URL}/token/refresh/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ refresh: refreshToken }),
        });

        const result = await response.json();
        if (response.ok) {
            localStorage.setItem('accessToken', result.access);
            console.log("Token refreshed successfully.");
            return result.access;
        } else {
            console.error("Token refresh failed:", result);
            logoutUser(); // If refresh token is invalid/expired, log out
            return null;
        }
    } catch (error) {
        console.error("Network error during token refresh:", error);
        return null;
    }
};

/**
 * A wrapper for fetch that automatically handles token expiration and refreshing.
 * Use this for all authenticated API calls.
 * @param {string} url - The URL to fetch.
 * @param {object} options - The options for the fetch request.
 * @returns {Promise<Response>}
 */
const fetchWithAuth = async (url, options = {}) => {
    let { accessToken } = getAuthData();

    if (!accessToken) {
        logoutUser();
        throw new Error("User not authenticated.");
    }
    
    const decodedToken = decodeJwt(accessToken);
    const isExpired = decodedToken ? (decodedToken.exp * 1000) < Date.now() : true;

    if (isExpired) {
        accessToken = await refreshAccessToken();
        if (!accessToken) {
            throw new Error("Session expired. Please log in again.");
        }
    }

    const headers = {
        ...options.headers,
        'Authorization': `Bearer ${accessToken}`,
        'Content-Type': 'application/json',
    };

    return fetch(`${API_BASE_URL}${url}`, { ...options, headers });
};


/**
 * Handles the user logout process.
 */
const logoutUser = async () => {
    const { refreshToken } = getAuthData();
    if (refreshToken) {
        try {
            await fetch(`${API_BASE_URL}/users/logout/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ refresh: refreshToken }),
            });
        } catch (error) {
            console.error('Logout API call failed, but logging out client-side anyway.', error);
        }
    }
    clearAuthData();
    window.location.href = '/index.html';
};

/**
 * Renders the header for a logged-in user.
 */
const renderLoggedInHeader = (user) => {
    const loggedOutView = document.getElementById('logged-out-view');
    const loggedInView = document.getElementById('logged-in-view');
    const logoutButton = document.getElementById('logout-button');

    if (loggedOutView) loggedOutView.classList.add('hidden');
    if (loggedInView) {
        loggedInView.classList.remove('hidden');
        if (logoutButton) {
            logoutButton.replaceWith(logoutButton.cloneNode(true));
            document.getElementById('logout-button').addEventListener('click', logoutUser);
        }
    }
};

/**
 * Renders the header for a logged-out visitor.
 */
const renderLoggedOutHeader = () => {
    const loggedOutView = document.getElementById('logged-out-view');
    const loggedInView = document.getElementById('logged-in-view');
    if (loggedOutView) loggedOutView.classList.remove('hidden');
    if (loggedInView) loggedInView.classList.add('hidden');
};

/**
 * Checks the user's login state on every page load and updates the UI.
 */
const checkLoginState = () => {
    const { user, accessToken } = getAuthData();
    if (user && accessToken) {
        renderLoggedInHeader(user);
    } else {
        renderLoggedOutHeader();
    }
};

// --- Main Execution ---
document.addEventListener('DOMContentLoaded', () => {
    checkLoginState();
});
