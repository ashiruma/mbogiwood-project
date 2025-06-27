// static/js/auth.js

document.addEventListener('DOMContentLoaded', () => {
    const API_BASE = '/api/v1/users'; // Adjust if your URL structure is different
    const loginForm = document.getElementById('login-form');
    const registerForm = document.getElementById('register-form');
    const authMessage = document.getElementById('auth-message');

    // Function to handle API responses and display messages
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
                    window.location.href = '/account.html'; // Redirect to the account dashboard
                } else {
                    showMessage(result.detail || 'An error occurred.', true);
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

            // Basic password validation (can be enhanced)
            // if (data.password !== data.confirm_password) {
            //     showMessage('Passwords do not match.', true);
            //     return;
            // }

            try {
                const response = await fetch(`${API_BASE}/signup/`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data),
                });

                const result = await response.json();

                if (response.status === 201) {
                    showMessage(result.detail, false);
                    registerForm.reset();
                } else {
                    showMessage(result.detail || 'Registration failed.', true);
                }
            } catch (error) {
                showMessage('Network error. Please try again.', true);
            }
        });
    }
});
