
// Recruitment System JavaScript Utilities

// Global state
window.RecruitmentApp = {
    user: null,
    token: null,
    
    init: function() {
        this.loadUserFromStorage();
        this.setupEventListeners();
    },
    
    loadUserFromStorage: function() {
        const token = localStorage.getItem('access_token');
        const user = localStorage.getItem('user');
        
        if (token && user) {
            this.token = token;
            this.user = JSON.parse(user);
            this.updateNavigation();
        }
    },
    
    updateNavigation: function() {
        // Update navigation based on user state
        if (this.user) {
            const navbarNav = document.querySelector('.navbar-nav');
            if (navbarNav) {
                navbarNav.innerHTML = `
                    <a class="nav-link" href="/">Home</a>
                    <a class="nav-link" href="/jobs">Jobs</a>
                    <a class="nav-link" href="/dashboard">Dashboard</a>
                    <a class="nav-link" href="#" onclick="RecruitmentApp.logout()">Logout (${this.user.firstname})</a>
                `;
            }
        }
    },
    
    setupEventListeners: function() {
        // Setup global event listeners
        document.addEventListener('DOMContentLoaded', () => {
            this.updateNavigation();
        });
    },
    
    logout: function() {
        localStorage.removeItem('access_token');
        localStorage.removeItem('user');
        this.token = null;
        this.user = null;
        window.location.href = '/';
    },
    
    makeAuthenticatedRequest: async function(url, options = {}) {
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            }
        };
        
        if (this.token) {
            defaultOptions.headers['Authorization'] = `Bearer ${this.token}`;
        }
        
        const response = await fetch(url, { ...defaultOptions, ...options });
        
        if (response.status === 401) {
            // Token expired or invalid
            this.logout();
            throw new Error('Authentication required');
        }
        
        return response;
    },
    
    showAlert: function(message, type = 'info', containerId = 'alertContainer') {
        const container = document.getElementById(containerId);
        if (!container) return;
        
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        container.appendChild(alertDiv);
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 5000);
    },
    
    formatDate: function(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
    },
    
    formatCurrency: function(amount, currency = 'USD') {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: currency
        }).format(amount);
    }
};

// Initialize the app
RecruitmentApp.init();

// Utility functions
function showLoading(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.classList.add('loading');
    }
}

function hideLoading(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.classList.remove('loading');
    }
}

function validateForm(formId) {
    const form = document.getElementById(formId);
    if (!form) return false;
    
    const inputs = form.querySelectorAll('input[required], select[required], textarea[required]');
    let isValid = true;
    
    inputs.forEach(input => {
        if (!input.value.trim()) {
            input.classList.add('is-invalid');
            isValid = false;
        } else {
            input.classList.remove('is-invalid');
        }
    });
    
    return isValid;
}

// Export for use in other scripts
window.showLoading = showLoading;
window.hideLoading = hideLoading;
window.validateForm = validateForm;
