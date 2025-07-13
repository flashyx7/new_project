
// Recruitment System Frontend JavaScript
// Enhanced with proper error handling and functionality

class RecruitmentApp {
    constructor() {
        this.apiBase = '';
        this.authToken = localStorage.getItem('authToken');
        this.currentUser = null;
        this.init();
    }

    init() {
        console.log('Initializing Recruitment App...');
        this.bindEvents();
        this.checkAuthStatus();
        this.loadServiceStatus();
        
        // Initialize forms if they exist
        if (document.getElementById('loginForm')) {
            this.initializeLoginForm();
        }
        if (document.getElementById('registerForm')) {
            this.initializeRegisterForm();
        }
        if (document.getElementById('applicationForm')) {
            this.initializeApplicationForm();
        }
    }

    bindEvents() {
        // Navigation events
        document.querySelectorAll('a[href^="#"]').forEach(link => {
            link.addEventListener('click', this.handleNavigation.bind(this));
        });

        // Form submission events
        document.addEventListener('submit', this.handleFormSubmit.bind(this));
        
        // Button click events
        document.addEventListener('click', this.handleButtonClick.bind(this));
    }

    handleNavigation(e) {
        e.preventDefault();
        const target = e.target.getAttribute('href');
        if (target === '#login') {
            this.showLoginModal();
        } else if (target === '#register') {
            this.showRegisterModal();
        }
    }

    async handleFormSubmit(e) {
        if (e.target.id === 'loginForm') {
            e.preventDefault();
            await this.handleLogin(e.target);
        } else if (e.target.id === 'registerForm') {
            e.preventDefault();
            await this.handleRegister(e.target);
        } else if (e.target.id === 'applicationForm') {
            e.preventDefault();
            await this.handleJobApplication(e.target);
        }
    }

    handleButtonClick(e) {
        if (e.target.classList.contains('btn-login')) {
            this.showLoginModal();
        } else if (e.target.classList.contains('btn-register')) {
            this.showRegisterModal();
        } else if (e.target.id === 'logoutBtn') {
            this.handleLogout();
        }
    }

    // Authentication Methods
    async handleLogin(form) {
        try {
            this.showLoading('Authenticating...');
            
            const formData = new FormData(form);
            const credentials = {
                username: formData.get('username'),
                password: formData.get('password')
            };

            const response = await fetch('/auth/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(credentials)
            });

            const result = await response.json();

            if (response.ok && result.token) {
                localStorage.setItem('authToken', result.token);
                this.authToken = result.token;
                this.showSuccess('Login successful! Redirecting...');
                
                setTimeout(() => {
                    window.location.href = '/application';
                }, 1500);
            } else {
                this.showError(result.message || 'Login failed');
            }
        } catch (error) {
            console.error('Login error:', error);
            this.showError('Login failed. Please try again.');
        } finally {
            this.hideLoading();
        }
    }

    async handleRegister(form) {
        try {
            this.showLoading('Creating account...');
            
            const formData = new FormData(form);
            const userData = {
                firstname: formData.get('firstname'),
                lastname: formData.get('lastname'),
                email: formData.get('email'),
                date_of_birth: formData.get('date_of_birth'),
                username: formData.get('username'),
                password: formData.get('password'),
                role_id: parseInt(formData.get('role_id')) || 2
            };

            // Client-side validation
            if (!this.validateRegistrationData(userData)) {
                return;
            }

            const response = await fetch('/registration/register', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(userData)
            });

            const result = await response.json();

            if (response.ok) {
                this.showSuccess('Registration successful! Please login.');
                setTimeout(() => {
                    this.showLoginModal();
                }, 2000);
            } else {
                this.showError(result.message || 'Registration failed');
            }
        } catch (error) {
            console.error('Registration error:', error);
            this.showError('Registration failed. Please try again.');
        } finally {
            this.hideLoading();
        }
    }

    validateRegistrationData(data) {
        if (!data.firstname || data.firstname.length < 2) {
            this.showError('First name must be at least 2 characters long');
            return false;
        }
        if (!data.lastname || data.lastname.length < 2) {
            this.showError('Last name must be at least 2 characters long');
            return false;
        }
        if (!data.email || !this.isValidEmail(data.email)) {
            this.showError('Please enter a valid email address');
            return false;
        }
        if (!data.username || data.username.length < 3) {
            this.showError('Username must be at least 3 characters long');
            return false;
        }
        if (!data.password || data.password.length < 6) {
            this.showError('Password must be at least 6 characters long');
            return false;
        }
        return true;
    }

    isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }

    handleLogout() {
        localStorage.removeItem('authToken');
        this.authToken = null;
        this.currentUser = null;
        window.location.href = '/';
    }

    // Job Application Methods
    async handleJobApplication(form) {
        try {
            if (!this.authToken) {
                this.showError('Please login first');
                return;
            }

            this.showLoading('Submitting application...');
            
            const formData = new FormData(form);
            const applicationData = {
                person_id: parseInt(formData.get('person_id')),
                availability: {
                    from_date: formData.get('from_date'),
                    to_date: formData.get('to_date')
                },
                competences: this.getSelectedCompetences(form)
            };

            const response = await fetch('/jobapplications/applications', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.authToken}`
                },
                body: JSON.stringify(applicationData)
            });

            const result = await response.json();

            if (response.ok) {
                this.showSuccess('Application submitted successfully!');
                setTimeout(() => {
                    window.location.href = '/application_list';
                }, 2000);
            } else {
                this.showError(result.message || 'Application submission failed');
            }
        } catch (error) {
            console.error('Application error:', error);
            this.showError('Application submission failed. Please try again.');
        } finally {
            this.hideLoading();
        }
    }

    getSelectedCompetences(form) {
        const competences = [];
        const competenceInputs = form.querySelectorAll('input[name^="competence_"]');
        
        competenceInputs.forEach(input => {
            if (input.checked || input.value) {
                const competenceId = input.name.replace('competence_', '');
                const experienceInput = form.querySelector(`input[name="experience_${competenceId}"]`);
                
                competences.push({
                    competence_id: parseInt(competenceId),
                    years_of_experience: parseFloat(experienceInput?.value || 0)
                });
            }
        });
        
        return competences;
    }

    // UI Methods
    showLoginModal() {
        const modal = this.createModal('Login', this.getLoginFormHTML());
        document.body.appendChild(modal);
        modal.style.display = 'block';
    }

    showRegisterModal() {
        const modal = this.createModal('Register', this.getRegisterFormHTML());
        document.body.appendChild(modal);
        modal.style.display = 'block';
    }

    createModal(title, content) {
        const modal = document.createElement('div');
        modal.className = 'modal fade show';
        modal.style.display = 'none';
        modal.innerHTML = `
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">${title}</h5>
                        <button type="button" class="btn-close" onclick="this.closest('.modal').remove()"></button>
                    </div>
                    <div class="modal-body">
                        ${content}
                    </div>
                </div>
            </div>
        `;
        return modal;
    }

    getLoginFormHTML() {
        return `
            <form id="loginForm">
                <div class="mb-3">
                    <label for="username" class="form-label">Username</label>
                    <input type="text" class="form-control" name="username" required>
                </div>
                <div class="mb-3">
                    <label for="password" class="form-label">Password</label>
                    <input type="password" class="form-control" name="password" required>
                </div>
                <button type="submit" class="btn btn-primary w-100">Login</button>
            </form>
        `;
    }

    getRegisterFormHTML() {
        return `
            <form id="registerForm">
                <div class="row">
                    <div class="col-md-6 mb-3">
                        <label for="firstname" class="form-label">First Name</label>
                        <input type="text" class="form-control" name="firstname" required>
                    </div>
                    <div class="col-md-6 mb-3">
                        <label for="lastname" class="form-label">Last Name</label>
                        <input type="text" class="form-control" name="lastname" required>
                    </div>
                </div>
                <div class="mb-3">
                    <label for="email" class="form-label">Email</label>
                    <input type="email" class="form-control" name="email" required>
                </div>
                <div class="mb-3">
                    <label for="date_of_birth" class="form-label">Date of Birth</label>
                    <input type="date" class="form-control" name="date_of_birth" required>
                </div>
                <div class="mb-3">
                    <label for="username" class="form-label">Username</label>
                    <input type="text" class="form-control" name="username" required>
                </div>
                <div class="mb-3">
                    <label for="password" class="form-label">Password</label>
                    <input type="password" class="form-control" name="password" required>
                </div>
                <div class="mb-3">
                    <label for="role_id" class="form-label">Role</label>
                    <select class="form-control" name="role_id">
                        <option value="2">Job Applicant</option>
                        <option value="1">Recruiter</option>
                    </select>
                </div>
                <button type="submit" class="btn btn-success w-100">Register</button>
            </form>
        `;
    }

    // Service Status
    async loadServiceStatus() {
        try {
            const services = [
                { name: 'Discovery Service', url: '/health', port: '9090' },
                { name: 'Config Service', url: '/health', port: '9091' },
                { name: 'Auth Service', url: '/auth/health', port: '8081' },
                { name: 'Registration Service', url: '/registration/health', port: '8888' },
                { name: 'Job Application Service', url: '/jobapplications/health', port: '8082' }
            ];

            const statusContainer = document.getElementById('servicesStatus');
            if (!statusContainer) return;

            for (const service of services) {
                try {
                    const response = await fetch(service.url, { timeout: 5000 });
                    const isHealthy = response.ok;
                    this.updateServiceStatus(service.name, isHealthy);
                } catch (error) {
                    this.updateServiceStatus(service.name, false);
                }
            }
        } catch (error) {
            console.error('Failed to load service status:', error);
        }
    }

    updateServiceStatus(serviceName, isHealthy) {
        const statusContainer = document.getElementById('servicesStatus');
        if (!statusContainer) return;

        const statusElement = Array.from(statusContainer.children)
            .find(el => el.textContent.includes(serviceName));
            
        if (statusElement) {
            const badge = statusElement.querySelector('.badge');
            if (badge) {
                badge.className = `badge ${isHealthy ? 'bg-success' : 'bg-danger'}`;
                badge.textContent = isHealthy ? 'Healthy' : 'Offline';
            }
        }
    }

    // Utility Methods
    checkAuthStatus() {
        if (this.authToken) {
            try {
                const payload = JSON.parse(atob(this.authToken.split('.')[1]));
                if (payload.exp * 1000 > Date.now()) {
                    this.currentUser = payload;
                    this.updateUIForAuthenticatedUser();
                } else {
                    localStorage.removeItem('authToken');
                    this.authToken = null;
                }
            } catch (error) {
                localStorage.removeItem('authToken');
                this.authToken = null;
            }
        }
    }

    updateUIForAuthenticatedUser() {
        const loginButtons = document.querySelectorAll('.btn-login');
        const registerButtons = document.querySelectorAll('.btn-register');
        
        loginButtons.forEach(btn => {
            btn.textContent = 'Dashboard';
            btn.onclick = () => window.location.href = '/application';
        });
        
        registerButtons.forEach(btn => btn.style.display = 'none');
    }

    showLoading(message = 'Loading...') {
        this.hideMessages();
        const loading = document.createElement('div');
        loading.id = 'loadingMessage';
        loading.className = 'alert alert-info';
        loading.innerHTML = `<i class="fas fa-spinner fa-spin"></i> ${message}`;
        document.body.appendChild(loading);
    }

    hideLoading() {
        const loading = document.getElementById('loadingMessage');
        if (loading) loading.remove();
    }

    showSuccess(message) {
        this.showMessage(message, 'success');
    }

    showError(message) {
        this.showMessage(message, 'danger');
    }

    showMessage(message, type = 'info') {
        this.hideMessages();
        const messageEl = document.createElement('div');
        messageEl.className = `alert alert-${type} alert-dismissible fade show`;
        messageEl.innerHTML = `
            ${message}
            <button type="button" class="btn-close" onclick="this.parentElement.remove()"></button>
        `;
        document.body.appendChild(messageEl);
        
        setTimeout(() => messageEl.remove(), 5000);
    }

    hideMessages() {
        document.querySelectorAll('.alert').forEach(alert => alert.remove());
    }

    // Form initialization
    initializeLoginForm() {
        const form = document.getElementById('loginForm');
        if (form) {
            form.addEventListener('submit', (e) => {
                e.preventDefault();
                this.handleLogin(form);
            });
        }
    }

    initializeRegisterForm() {
        const form = document.getElementById('registerForm');
        if (form) {
            form.addEventListener('submit', (e) => {
                e.preventDefault();
                this.handleRegister(form);
            });
        }
    }

    initializeApplicationForm() {
        const form = document.getElementById('applicationForm');
        if (form) {
            form.addEventListener('submit', (e) => {
                e.preventDefault();
                this.handleJobApplication(form);
            });
            
            // Load competences and other data
            this.loadApplicationFormData();
        }
    }

    async loadApplicationFormData() {
        try {
            // Load competences
            const competencesResponse = await fetch('/jobapplications/competences');
            if (competencesResponse.ok) {
                const competences = await competencesResponse.json();
                this.populateCompetences(competences);
            }
        } catch (error) {
            console.error('Failed to load form data:', error);
        }
    }

    populateCompetences(competences) {
        const container = document.getElementById('competencesContainer');
        if (!container) return;

        container.innerHTML = competences.map(comp => `
            <div class="col-md-6 mb-2">
                <div class="form-check">
                    <input class="form-check-input" type="checkbox" 
                           name="competence_${comp.id}" id="comp_${comp.id}">
                    <label class="form-check-label" for="comp_${comp.id}">
                        ${comp.name}
                    </label>
                    <input type="number" class="form-control form-control-sm mt-1" 
                           name="experience_${comp.id}" placeholder="Years of experience" 
                           min="0" max="50" step="0.5" style="display:none;">
                </div>
            </div>
        `).join('');

        // Show experience input when competence is selected
        container.querySelectorAll('input[type="checkbox"]').forEach(checkbox => {
            checkbox.addEventListener('change', (e) => {
                const experienceInput = e.target.parentElement.querySelector('input[type="number"]');
                experienceInput.style.display = e.target.checked ? 'block' : 'none';
                if (!e.target.checked) experienceInput.value = '';
            });
        });
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    try {
        window.recruitmentApp = new RecruitmentApp();
    } catch (error) {
        console.error('Failed to initialize application:', error);
    }
});

// Prevent unhandled promise rejections
window.addEventListener('unhandledrejection', (event) => {
    console.error('Unhandled promise rejection:', event.reason);
    event.preventDefault();
});
