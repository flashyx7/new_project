// Application JavaScript for Recruitment System

// Global variables
let currentUser = null;

// Initialize application
document.addEventListener('DOMContentLoaded', function() {
    console.log('Application initialized');

    // Initialize dark mode
    initializeDarkMode();

    // Initialize forms
    initializeForms();

    // Load user data if logged in
    loadCurrentUser();
});

// Dark mode functionality
function initializeDarkMode() {
    const darkModeToggle = document.getElementById('darkModeToggle');
    if (darkModeToggle) {
        // Check saved preference
        const isDarkMode = localStorage.getItem('darkMode') === 'true';
        if (isDarkMode) {
            document.body.classList.add('dark-mode');
            darkModeToggle.checked = true;
        }

        darkModeToggle.addEventListener('change', function() {
            if (this.checked) {
                document.body.classList.add('dark-mode');
                localStorage.setItem('darkMode', 'true');
            } else {
                document.body.classList.remove('dark-mode');
                localStorage.setItem('darkMode', 'false');
            }
        });
    }
}

// Initialize forms
function initializeForms() {
    // Login form
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', handleLogin);
    }

    // Registration form
    const registerForm = document.getElementById('registerForm');
    if (registerForm) {
        registerForm.addEventListener('submit', handleRegistration);
    }
}

// Handle login
async function handleLogin(event) {
    event.preventDefault();

    const formData = new FormData(event.target);
    const loginData = {
        username: formData.get('username'),
        password: formData.get('password')
    };

    try {
        const response = await fetch('/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: new URLSearchParams(loginData)
        });

        if (response.ok) {
            window.location.href = '/dashboard';
        } else {
            showMessage('error', 'Login failed. Please check your credentials.');
        }
    } catch (error) {
        console.error('Login error:', error);
        showMessage('error', 'Login failed. Please try again.');
    }
}

// Handle registration
async function handleRegistration(event) {
    event.preventDefault();

    const formData = new FormData(event.target);
    const registerData = {
        firstname: formData.get('firstname'),
        lastname: formData.get('lastname'),
        email: formData.get('email'),
        username: formData.get('username'),
        password: formData.get('password')
    };

    try {
        const response = await fetch('/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: new URLSearchParams(registerData)
        });

        if (response.ok) {
            window.location.href = '/login?message=Registration successful';
        } else {
            showMessage('error', 'Registration failed. Please try again.');
        }
    } catch (error) {
        console.error('Registration error:', error);
        showMessage('error', 'Registration failed. Please try again.');
    }
}

// Load current user
async function loadCurrentUser() {
    try {
        const response = await fetch('/api/user/current');
        if (response.ok) {
            currentUser = await response.json();
        }
    } catch (error) {
        console.log('No user session found');
    }
}

// Show message
function showMessage(type, message) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type === 'error' ? 'danger' : 'success'} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;

    const container = document.querySelector('.container');
    if (container) {
        container.insertBefore(alertDiv, container.firstChild);

        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            alertDiv.remove();
        }, 5000);
    }
}

// Export functions for global access
window.showMessage = showMessage;
window.handleLogin = handleLogin;
window.handleRegistration = handleRegistration;