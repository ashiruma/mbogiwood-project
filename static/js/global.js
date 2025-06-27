// static/js/global.js

// --- Constants ---
const API_BASE_URL = '/api/v1'; // Adjust if your URL structure is different

// --- Utility Functions ---

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
        // In case of parsing errors, return null
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
 * Handles the user logout process.
 */
const logoutUser = async () => {
    const { refreshToken } = getAuthData();
    if (refreshToken) {
        try {
            // Ask the backend to blacklist the token
            await fetch(`${API_BASE_URL}/users/logout/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ refresh: refreshToken }),
            });
        } catch (error) {
            console.error('Logout API call failed, but logging out client-side anyway.', error);
        }
    }
    // Always clear local data and redirect
    clearAuthData();
    window.location.href = '/index.html'; // Redirect to homepage
};

/**
 * Renders the header for a logged-in user.
 * @param {object} user - The user data object.
 */
const renderLoggedInHeader = (user) => {
    const loggedOutView = document.getElementById('logged-out-view');
    const loggedInView = document.getElementById('logged-in-view');
    const logoutButton = document.getElementById('logout-button');

    if (loggedOutView) loggedOutView.classList.add('hidden');
    if (loggedInView) {
        loggedInView.classList.remove('hidden');
        if (logoutButton) {
            // Important: Remove old listeners to prevent duplicates before adding a new one.
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
        // In a production app, you would add logic here to check if the accessToken is expired
        // using a library like jwt-decode. If expired, you would trigger the silent refresh.
        // For now, we assume it's valid if it exists.
        renderLoggedInHeader(user);
    } else {
        renderLoggedOutHeader();
    }
};

// --- Main Execution ---
// This runs on every page that includes global.js
document.addEventListener('DOMContentLoaded', () => {
    checkLoginState();
});
