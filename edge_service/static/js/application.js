
// Recruitment System JavaScript Utilities

document.addEventListener('DOMContentLoaded', function() {
    // Initialize the application
    initializeApp();
});

function initializeApp() {
    // Set up event listeners
    setupEventListeners();
    
    // Initialize forms
    initializeForms();
    
    // Setup CSRF protection
    setupCSRF();
}

function setupEventListeners() {
    // Job application form submission
    const applyForms = document.querySelectorAll('.apply-form');
    applyForms.forEach(form => {
        form.addEventListener('submit', handleJobApplication);
    });
    
    // Login form validation
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', validateLoginForm);
    }
    
    // Registration form validation
    const registerForm = document.getElementById('registerForm');
    if (registerForm) {
        registerForm.addEventListener('submit', validateRegisterForm);
    }
    
    // Search functionality
    const searchInput = document.getElementById('jobSearch');
    if (searchInput) {
        searchInput.addEventListener('input', debounce(handleJobSearch, 300));
    }
}

function initializeForms() {
    // Initialize date pickers
    const dateInputs = document.querySelectorAll('input[type="date"]');
    dateInputs.forEach(input => {
        if (!input.value) {
            input.value = new Date().toISOString().split('T')[0];
        }
    });
    
    // Initialize file upload indicators
    const fileInputs = document.querySelectorAll('input[type="file"]');
    fileInputs.forEach(input => {
        input.addEventListener('change', handleFileUpload);
    });
}

function setupCSRF() {
    // Get CSRF token from meta tag or form
    const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');
    
    // Add CSRF token to all forms
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        if (csrfToken && !form.querySelector('input[name="csrf_token"]')) {
            const csrfInput = document.createElement('input');
            csrfInput.type = 'hidden';
            csrfInput.name = 'csrf_token';
            csrfInput.value = csrfToken;
            form.appendChild(csrfInput);
        }
    });
}

async function handleJobApplication(event) {
    event.preventDefault();
    
    const form = event.target;
    const formData = new FormData(form);
    const jobId = form.dataset.jobId;
    
    try {
        showLoading(true);
        
        const response = await fetch(`/jobs/${jobId}/apply`, {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (response.ok) {
            showMessage('Application submitted successfully!', 'success');
            form.reset();
            // Disable form to prevent duplicate submissions
            form.style.display = 'none';
            const successMsg = document.createElement('div');
            successMsg.className = 'alert alert-success';
            successMsg.textContent = 'Application already submitted';
            form.parentNode.insertBefore(successMsg, form);
        } else {
            showMessage(result.detail || 'Application failed', 'error');
        }
    } catch (error) {
        console.error('Application error:', error);
        showMessage('An error occurred. Please try again.', 'error');
    } finally {
        showLoading(false);
    }
}

function validateLoginForm(event) {
    const form = event.target;
    const username = form.querySelector('input[name="username"]').value.trim();
    const password = form.querySelector('input[name="password"]').value;
    
    if (!username) {
        showMessage('Username is required', 'error');
        event.preventDefault();
        return false;
    }
    
    if (!password) {
        showMessage('Password is required', 'error');
        event.preventDefault();
        return false;
    }
    
    return true;
}

function validateRegisterForm(event) {
    const form = event.target;
    const password = form.querySelector('input[name="password"]').value;
    const email = form.querySelector('input[name="email"]').value;
    
    // Password validation
    if (password.length < 6) {
        showMessage('Password must be at least 6 characters long', 'error');
        event.preventDefault();
        return false;
    }
    
    // Email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
        showMessage('Please enter a valid email address', 'error');
        event.preventDefault();
        return false;
    }
    
    return true;
}

function handleJobSearch(event) {
    const searchTerm = event.target.value.toLowerCase();
    const jobCards = document.querySelectorAll('.job-card');
    
    jobCards.forEach(card => {
        const title = card.querySelector('.job-title')?.textContent.toLowerCase() || '';
        const description = card.querySelector('.job-description')?.textContent.toLowerCase() || '';
        const location = card.querySelector('.job-location')?.textContent.toLowerCase() || '';
        
        if (title.includes(searchTerm) || description.includes(searchTerm) || location.includes(searchTerm)) {
            card.style.display = 'block';
        } else {
            card.style.display = 'none';
        }
    });
}

function handleFileUpload(event) {
    const input = event.target;
    const file = input.files[0];
    
    if (file) {
        // Validate file size (5MB limit)
        if (file.size > 5 * 1024 * 1024) {
            showMessage('File size must be less than 5MB', 'error');
            input.value = '';
            return;
        }
        
        // Validate file type for resumes
        const allowedTypes = ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
        if (input.name === 'resume' && !allowedTypes.includes(file.type)) {
            showMessage('Please upload a PDF or Word document for your resume', 'error');
            input.value = '';
            return;
        }
        
        // Show file name
        const fileLabel = input.parentNode.querySelector('.file-label');
        if (fileLabel) {
            fileLabel.textContent = file.name;
        }
    }
}

function showMessage(message, type = 'info') {
    // Remove existing messages
    const existingMessages = document.querySelectorAll('.alert-message');
    existingMessages.forEach(msg => msg.remove());
    
    // Create new message
    const messageDiv = document.createElement('div');
    messageDiv.className = `alert alert-${type} alert-message`;
    messageDiv.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 1000;
        padding: 15px;
        border-radius: 4px;
        max-width: 400px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    `;
    
    // Set colors based on type
    switch (type) {
        case 'success':
            messageDiv.style.backgroundColor = '#d4edda';
            messageDiv.style.color = '#155724';
            messageDiv.style.border = '1px solid #c3e6cb';
            break;
        case 'error':
            messageDiv.style.backgroundColor = '#f8d7da';
            messageDiv.style.color = '#721c24';
            messageDiv.style.border = '1px solid #f5c6cb';
            break;
        default:
            messageDiv.style.backgroundColor = '#d1ecf1';
            messageDiv.style.color = '#0c5460';
            messageDiv.style.border = '1px solid #bee5eb';
    }
    
    messageDiv.textContent = message;
    
    // Add close button
    const closeBtn = document.createElement('button');
    closeBtn.innerHTML = '&times;';
    closeBtn.style.cssText = `
        background: none;
        border: none;
        font-size: 18px;
        font-weight: bold;
        float: right;
        line-height: 1;
        color: inherit;
        cursor: pointer;
        margin-left: 10px;
    `;
    closeBtn.onclick = () => messageDiv.remove();
    messageDiv.appendChild(closeBtn);
    
    document.body.appendChild(messageDiv);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (messageDiv.parentNode) {
            messageDiv.remove();
        }
    }, 5000);
}

function showLoading(show) {
    let loadingDiv = document.getElementById('loading-overlay');
    
    if (show) {
        if (!loadingDiv) {
            loadingDiv = document.createElement('div');
            loadingDiv.id = 'loading-overlay';
            loadingDiv.style.cssText = `
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0,0,0,0.5);
                display: flex;
                justify-content: center;
                align-items: center;
                z-index: 9999;
            `;
            
            const spinner = document.createElement('div');
            spinner.style.cssText = `
                border: 4px solid #f3f3f3;
                border-top: 4px solid #3498db;
                border-radius: 50%;
                width: 50px;
                height: 50px;
                animation: spin 1s linear infinite;
            `;
            
            // Add CSS animation
            const style = document.createElement('style');
            style.textContent = `
                @keyframes spin {
                    0% { transform: rotate(0deg); }
                    100% { transform: rotate(360deg); }
                }
            `;
            document.head.appendChild(style);
            
            loadingDiv.appendChild(spinner);
            document.body.appendChild(loadingDiv);
        }
        loadingDiv.style.display = 'flex';
    } else {
        if (loadingDiv) {
            loadingDiv.style.display = 'none';
        }
    }
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Utility functions for API calls
async function apiCall(url, options = {}) {
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
        },
    };
    
    const finalOptions = { ...defaultOptions, ...options };
    
    try {
        const response = await fetch(url, finalOptions);
        return response;
    } catch (error) {
        console.error('API call failed:', error);
        throw error;
    }
}

// Export functions for use in other scripts
window.RecruitmentApp = {
    showMessage,
    showLoading,
    apiCall,
    handleJobApplication
};
