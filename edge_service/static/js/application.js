// Frontend JavaScript for the Recruitment System

class RecruitmentApp {
    constructor() {
        this.initializeEventListeners();
        this.loadJobs();
    }

    initializeEventListeners() {
        // Login form
        const loginForm = document.getElementById('loginForm');
        if (loginForm) {
            loginForm.addEventListener('submit', (e) => this.handleLogin(e));
        }

        // Registration form
        const registerForm = document.getElementById('registerForm');
        if (registerForm) {
            registerForm.addEventListener('submit', (e) => this.handleRegistration(e));
        }

        // Job application forms
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('apply-btn')) {
                this.handleJobApplication(e);
            }
        });
    }

    async handleLogin(event) {
        event.preventDefault();

        const form = event.target;
        const formData = new FormData(form);

        try {
            const response = await fetch('/api/auth/login', {
                method: 'POST',
                body: formData
            });

            const result = await response.json();

            if (response.ok) {
                // Success - redirect to dashboard
                window.location.href = '/dashboard';
            } else {
                // Show error
                this.showError('loginError', result.error || 'Login failed');
            }
        } catch (error) {
            console.error('Login error:', error);
            this.showError('loginError', 'Network error. Please try again.');
        }
    }

    async handleRegistration(event) {
        event.preventDefault();

        const form = event.target;
        const formData = new FormData(form);

        // Validate passwords match
        const password = formData.get('password');
        const confirmPassword = formData.get('confirm_password');

        if (password !== confirmPassword) {
            this.showError('registerError', 'Passwords do not match');
            return;
        }

        try {
            const response = await fetch('/api/auth/register', {
                method: 'POST',
                body: formData
            });

            const result = await response.json();

            if (response.ok) {
                // Success - redirect to login
                window.location.href = '/login?message=Registration successful';
            } else {
                // Show error
                this.showError('registerError', result.error || 'Registration failed');
            }
        } catch (error) {
            console.error('Registration error:', error);
            this.showError('registerError', 'Network error. Please try again.');
        }
    }

    async handleJobApplication(event) {
        event.preventDefault();

        const jobId = event.target.dataset.jobId;
        const coverLetter = prompt('Please enter a cover letter for this application:');

        if (!coverLetter) {
            return;
        }

        try {
            const formData = new FormData();
            formData.append('cover_letter', coverLetter);

            const response = await fetch(`/jobs/${jobId}/apply`, {
                method: 'POST',
                body: formData
            });

            const result = await response.json();

            if (response.ok) {
                alert('Application submitted successfully!');
                event.target.disabled = true;
                event.target.textContent = 'Applied';
            } else {
                alert(result.detail || 'Application failed');
            }
        } catch (error) {
            console.error('Application error:', error);
            alert('Network error. Please try again.');
        }
    }

    async loadJobs() {
        const jobsContainer = document.getElementById('jobsContainer');
        if (!jobsContainer) return;

        try {
            const response = await fetch('/api/jobs');
            const data = await response.json();

            if (response.ok && data.jobs) {
                this.renderJobs(data.jobs, jobsContainer);
            } else {
                jobsContainer.innerHTML = '<p class="error">Failed to load jobs</p>';
            }
        } catch (error) {
            console.error('Error loading jobs:', error);
            jobsContainer.innerHTML = '<p class="error">Network error loading jobs</p>';
        }
    }

    renderJobs(jobs, container) {
        if (jobs.length === 0) {
            container.innerHTML = '<p>No jobs available at the moment.</p>';
            return;
        }

        const jobsHtml = jobs.map(job => `
            <div class="job-card">
                <h3>${this.escapeHtml(job.title)}</h3>
                <p class="job-location">${this.escapeHtml(job.location || 'Not specified')}</p>
                <p class="job-description">${this.escapeHtml(job.description)}</p>
                ${job.salary_min && job.salary_max ? 
                    `<p class="job-salary">$${job.salary_min.toLocaleString()} - $${job.salary_max.toLocaleString()}</p>` : 
                    ''
                }
                <p class="job-type">${this.escapeHtml(job.employment_type || 'full-time')} • ${this.escapeHtml(job.experience_level || 'mid')}</p>
                <button class="apply-btn" data-job-id="${job.id}">Apply Now</button>
            </div>
        `).join('');

        container.innerHTML = jobsHtml;
    }

    showError(elementId, message) {
        const errorElement = document.getElementById(elementId);
        if (errorElement) {
            errorElement.textContent = message;
            errorElement.style.display = 'block';
        } else {
            alert(message);
        }
    }

    escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize the app when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new RecruitmentApp();
});