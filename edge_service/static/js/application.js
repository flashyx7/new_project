
// Application JavaScript
document.addEventListener('DOMContentLoaded', function() {
    console.log('Application JavaScript loaded');

    // Handle login form
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', handleLogin);
    }

    // Handle registration form
    const registerForm = document.getElementById('registerForm');
    if (registerForm) {
        registerForm.addEventListener('submit', handleRegistration);
    }

    // Handle job application forms
    const jobApplicationForms = document.querySelectorAll('.job-application-form');
    jobApplicationForms.forEach(form => {
        form.addEventListener('submit', handleJobApplication);
    });

    // Load jobs on jobs page
    if (window.location.pathname === '/jobs') {
        loadJobs();
    }
});

async function handleLogin(event) {
    event.preventDefault();
    
    const form = event.target;
    const formData = new FormData(form);
    const errorDiv = document.getElementById('loginError');
    const submitButton = form.querySelector('button[type="submit"]');
    
    // Clear previous errors
    if (errorDiv) {
        errorDiv.style.display = 'none';
        errorDiv.textContent = '';
    }

    // Disable submit button
    if (submitButton) {
        submitButton.disabled = true;
        submitButton.textContent = 'Logging in...';
    }

    try {
        const response = await fetch('/api/auth/login', {
            method: 'POST',
            body: formData
        });

        const result = await response.json();

        if (response.ok) {
            // Login successful
            window.location.href = '/dashboard';
        } else {
            // Login failed
            showError(errorDiv, result.error || 'Login failed');
        }
    } catch (error) {
        console.error('Login error:', error);
        showError(errorDiv, 'Network error. Please try again.');
    } finally {
        // Re-enable submit button
        if (submitButton) {
            submitButton.disabled = false;
            submitButton.textContent = 'Login';
        }
    }
}

async function handleRegistration(event) {
    event.preventDefault();
    
    const form = event.target;
    const formData = new FormData(form);
    const errorDiv = document.getElementById('registerError');
    const successDiv = document.getElementById('registerSuccess');
    const submitButton = form.querySelector('button[type="submit"]');
    
    // Clear previous messages
    if (errorDiv) {
        errorDiv.style.display = 'none';
        errorDiv.textContent = '';
    }
    if (successDiv) {
        successDiv.style.display = 'none';
        successDiv.textContent = '';
    }

    // Basic validation
    const password = formData.get('password');
    const confirmPassword = formData.get('confirmPassword');
    
    if (password !== confirmPassword) {
        showError(errorDiv, 'Passwords do not match');
        return;
    }

    if (password.length < 6) {
        showError(errorDiv, 'Password must be at least 6 characters long');
        return;
    }

    // Disable submit button
    if (submitButton) {
        submitButton.disabled = true;
        submitButton.textContent = 'Registering...';
    }

    try {
        const response = await fetch('/api/auth/register', {
            method: 'POST',
            body: formData
        });

        let result;
        try {
            result = await response.json();
        } catch (parseError) {
            console.error('Failed to parse response as JSON:', parseError);
            result = { error: 'Invalid response from server' };
        }

        if (response.ok) {
            // Registration successful
            showSuccess(successDiv, result.message || 'Registration successful! You can now login.');
            form.reset();
            
            // Redirect to login page after 2 seconds
            setTimeout(() => {
                window.location.href = '/login';
            }, 2000);
        } else {
            // Registration failed
            console.error('Registration failed:', result);
            showError(errorDiv, result.error || 'Registration failed. Please try again.');
        }
    } catch (error) {
        console.error('Registration error:', error);
        showError(errorDiv, 'Network error. Please try again.');
    } finally {
        // Re-enable submit button
        if (submitButton) {
            submitButton.disabled = false;
            submitButton.textContent = 'Register';
        }
    }
}

async function handleJobApplication(event) {
    event.preventDefault();
    
    const form = event.target;
    const formData = new FormData(form);
    const jobId = form.dataset.jobId;
    
    try {
        const response = await fetch(`/jobs/${jobId}/apply`, {
            method: 'POST',
            body: formData
        });

        const result = await response.json();

        if (response.ok) {
            alert('Application submitted successfully!');
            form.reset();
        } else {
            alert(result.detail || 'Application failed');
        }
    } catch (error) {
        console.error('Application error:', error);
        alert('Network error. Please try again.');
    }
}

async function loadJobs() {
    try {
        const response = await fetch('/api/jobs');
        const data = await response.json();
        
        if (response.ok && data.jobs) {
            displayJobs(data.jobs);
        } else {
            console.error('Failed to load jobs:', data);
        }
    } catch (error) {
        console.error('Error loading jobs:', error);
    }
}

function displayJobs(jobs) {
    const jobsContainer = document.getElementById('jobsContainer');
    if (!jobsContainer) return;

    if (jobs.length === 0) {
        jobsContainer.innerHTML = '<p>No jobs available at the moment.</p>';
        return;
    }

    jobsContainer.innerHTML = jobs.map(job => `
        <div class="job-card">
            <h3>${escapeHtml(job.title)}</h3>
            <p class="job-meta">
                <span>📍 ${escapeHtml(job.location || 'Remote')}</span>
                <span>💼 ${escapeHtml(job.employment_type || 'Full-time')}</span>
                <span>📊 ${escapeHtml(job.experience_level || 'Mid-level')}</span>
            </p>
            <p class="job-description">${escapeHtml(job.description)}</p>
            ${job.salary_min && job.salary_max ? 
                `<p class="job-salary">💰 $${job.salary_min.toLocaleString()} - $${job.salary_max.toLocaleString()}</p>` : 
                ''
            }
            <button onclick="showJobDetails(${job.id})" class="btn btn-primary">View Details</button>
        </div>
    `).join('');
}

function showJobDetails(jobId) {
    // This would show job details in a modal or navigate to a details page
    window.location.href = `/jobs/${jobId}`;
}

function showError(errorDiv, message) {
    if (errorDiv) {
        errorDiv.textContent = message;
        errorDiv.style.display = 'block';
        errorDiv.className = 'alert alert-danger';
    } else {
        alert(message);
    }
}

function showSuccess(successDiv, message) {
    if (successDiv) {
        successDiv.textContent = message;
        successDiv.style.display = 'block';
        successDiv.className = 'alert alert-success';
    } else {
        alert(message);
    }
}

function escapeHtml(unsafe) {
    return unsafe
         .replace(/&/g, "&amp;")
         .replace(/</g, "&lt;")
         .replace(/>/g, "&gt;")
         .replace(/"/g, "&quot;")
         .replace(/'/g, "&#039;");
}

// Utility functions
function showLoading(element) {
    if (element) {
        element.innerHTML = '<div class="loading">Loading...</div>';
    }
}

function hideLoading(element) {
    if (element) {
        const loading = element.querySelector('.loading');
        if (loading) {
            loading.remove();
        }
    }
}
