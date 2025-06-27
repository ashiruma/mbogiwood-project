// static/js/auth.js

document.addEventListener('DOMContentLoaded', () => {
    // This assumes global.js is also loaded on the page
    const API_BASE = '/api/v1/users';
    const loginForm = document.getElementById('login-form');
    const registerForm = document.getElementById('register-form');
    const authMessage = document.getElementById('auth-message');

    /**
     * Displays a message to the user in the designated message area.
     * @param {string} message - The message to display.
     * @param {boolean} isError - True if the message is an error, false for success/info.
     */
    const showMessage = (message, isError = false) => {
        if (authMessage) {
            authMessage.textContent = message;
            authMessage.className = isError 
                ? 'mt-4 text-center text-red-400 font-medium' 
                : 'mt-4 text-center text-green-400 font-medium';
        }
    };

    // --- Login Form Handler ---
    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            showMessage('Logging in...', false);

            const formData = new FormData(loginForm);
            const data = Object.fromEntries(formData.entries());

            try {
                const response = await fetch(`${API_BASE}/login/`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data),
                });

                const result = await response.json();

                if (response.ok) {
                    // Store tokens and user data upon successful login
                    localStorage.setItem('accessToken', result.access);
                    localStorage.setItem('refreshToken', result.refresh);
                    localStorage.setItem('userData', JSON.stringify(result.user));
                    
                    showMessage('Login successful! Redirecting...', false);
                    // Redirect to the account dashboard after successful login
                    window.location.href = '/account.html'; 
                } else {
                    showMessage(result.detail || 'Invalid credentials. Please try again.', true);
                }
            } catch (error) {
                showMessage('Network error. Please try again.', true);
            }
        });
    }

    // --- Register Form Handler ---
    if (registerForm) {
        registerForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            showMessage('Creating account...', false);

            const formData = new FormData(registerForm);
            const data = Object.fromEntries(formData.entries());
            data.is_creator = data.is_creator === 'on'; // Convert checkbox value to boolean

            try {
                const response = await fetch(`${API_BASE}/signup/`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data),
                });

                const result = await response.json();

                if (response.status === 201) {
                    // Display success message and clear the form
                    showMessage(result.detail, false);
                    registerForm.reset();
                } else {
                    // Display error message from the API
                    showMessage(result.detail || 'Registration failed. Please check your details and try again.', true);
                }
            } catch (error) {
                showMessage('Network error. Please try again.', true);
            }
        });
    }
});
