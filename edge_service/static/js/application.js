// Global variables
let currentUser = null;
let authToken = null;

// API Base URLs
const API_BASE = 'http://localhost:8080';
const AUTH_API = `${API_BASE}/auth`;
const REGISTRATION_API = `${API_BASE}/registration`;
const JOB_API = `${API_BASE}/job-application`;

// Utility functions
function showMessage(elementId, message, type = 'info') {
    const element = document.getElementById(elementId);
    if (element) {
        element.innerHTML = `
            <div class="alert alert-${type === 'error' ? 'danger' : type === 'success' ? 'success' : 'info'} alert-dismissible fade show" role="alert">
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;
    }
}

function showLoading(elementId, show = true) {
    const element = document.getElementById(elementId);
    if (element) {
        element.style.display = show ? 'inline-block' : 'none';
    }
}

function hideAllSections() {
    const sections = ['profileSection', 'applicationsSection', 'newApplicationSection', 'settingsSection'];
    sections.forEach(section => {
        const element = document.getElementById(section);
        if (element) {
            element.classList.add('hidden');
        }
    });
}

function updateNavigation() {
    const dashboardLink = document.getElementById('dashboardLink');
    const logoutLink = document.getElementById('logoutLink');
    
    if (currentUser && authToken) {
        if (dashboardLink) dashboardLink.style.display = 'inline-block';
        if (logoutLink) logoutLink.style.display = 'inline-block';
    } else {
        if (dashboardLink) dashboardLink.style.display = 'none';
        if (logoutLink) logoutLink.style.display = 'none';
    }
}

// Service status checking
async function checkServiceStatus() {
    const services = [
        { name: 'Discovery Service', url: 'http://localhost:9090/health' },
        { name: 'Config Service', url: 'http://localhost:9999/health' },
        { name: 'Auth Service', url: 'http://localhost:8081/health' },
        { name: 'Registration Service', url: 'http://localhost:8888/health' },
        { name: 'Job Application Service', url: 'http://localhost:8082/health' },
        { name: 'Edge Service', url: 'http://localhost:8080/health' }
    ];

    const statusContainer = document.getElementById('servicesStatus');
    if (!statusContainer) return;

    statusContainer.innerHTML = '';

    for (const service of services) {
        try {
            const response = await fetch(service.url);
            const isHealthy = response.ok;
            
            const statusHtml = `
                <div class="col-md-4 mb-3">
                    <div class="service-status ${isHealthy ? 'status-healthy' : 'status-error'}">
                        <h5><i class="fas fa-server me-2"></i>${service.name}</h5>
                        <p class="mb-0">Status: <span class="badge ${isHealthy ? 'bg-success' : 'bg-danger'}">${isHealthy ? 'Healthy' : 'Error'}</span></p>
                    </div>
                </div>
            `;
            statusContainer.innerHTML += statusHtml;
        } catch (error) {
            const statusHtml = `
                <div class="col-md-4 mb-3">
                    <div class="service-status status-error">
                        <h5><i class="fas fa-server me-2"></i>${service.name}</h5>
                        <p class="mb-0">Status: <span class="badge bg-danger">Error</span></p>
                    </div>
                </div>
            `;
            statusContainer.innerHTML += statusHtml;
        }
    }
}

// Registration functionality
document.addEventListener('DOMContentLoaded', function() {
    const registrationForm = document.getElementById('registrationForm');
    if (registrationForm) {
        registrationForm.addEventListener('submit', handleRegistration);
    }

    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', handleLogin);
    }

    const applicationForm = document.getElementById('applicationForm');
    if (applicationForm) {
        applicationForm.addEventListener('submit', handleApplicationSubmit);
    }

    // Check service status on page load
    checkServiceStatus();
    
    // Check for existing session
    const savedToken = localStorage.getItem('authToken');
    const savedUser = localStorage.getItem('currentUser');
    
    if (savedToken && savedUser) {
        authToken = savedToken;
        currentUser = JSON.parse(savedUser);
        updateNavigation();
    }
});

async function handleRegistration(event) {
    event.preventDefault();
    
    const spinner = document.getElementById('registerSpinner');
    const text = document.getElementById('registerText');
    
    showLoading('registerSpinner', true);
    text.textContent = 'Registering...';
    
    const formData = {
        firstname: document.getElementById('firstName').value,
        lastname: document.getElementById('lastName').value,
        email: document.getElementById('email').value,
        date_of_birth: document.getElementById('dateOfBirth').value,
        username: document.getElementById('username').value,
        password: document.getElementById('password').value,
        role_id: parseInt(document.getElementById('role').value)
    };

    try {
        const response = await fetch(`${REGISTRATION_API}/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });

        const result = await response.json();

        if (response.ok) {
            showMessage('registrationMessage', 'Registration successful! You can now login.', 'success');
            document.getElementById('registrationForm').reset();
        } else {
            showMessage('registrationMessage', `Registration failed: ${result.detail || 'Unknown error'}`, 'error');
        }
    } catch (error) {
        showMessage('registrationMessage', `Registration failed: ${error.message}`, 'error');
    } finally {
        showLoading('registerSpinner', false);
        text.textContent = 'Register';
    }
}

async function handleLogin(event) {
    event.preventDefault();
    
    const spinner = document.getElementById('loginSpinner');
    const text = document.getElementById('loginText');
    
    showLoading('loginSpinner', true);
    text.textContent = 'Logging in...';
    
    const formData = {
        username: document.getElementById('loginUsername').value,
        password: document.getElementById('loginPassword').value
    };

    try {
        const response = await fetch(`${AUTH_API}/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });

        const result = await response.json();

        if (response.ok) {
            authToken = result.token;
            currentUser = {
                username: formData.username,
                token: result.token
            };
            
            // Save to localStorage
            localStorage.setItem('authToken', authToken);
            localStorage.setItem('currentUser', JSON.stringify(currentUser));
            
            updateNavigation();
            showMessage('loginMessage', 'Login successful!', 'success');
            document.getElementById('loginForm').reset();
            
            // Show dashboard
            showDashboard();
        } else {
            showMessage('loginMessage', `Login failed: ${result.detail || 'Invalid credentials'}`, 'error');
        }
    } catch (error) {
        showMessage('loginMessage', `Login failed: ${error.message}`, 'error');
    } finally {
        showLoading('loginSpinner', false);
        text.textContent = 'Login';
    }
}

function logout() {
    authToken = null;
    currentUser = null;
    localStorage.removeItem('authToken');
    localStorage.removeItem('currentUser');
    updateNavigation();
    
    // Hide dashboard
    const dashboard = document.getElementById('dashboard');
    if (dashboard) {
        dashboard.classList.add('hidden');
    }
    
    // Show success message
    showMessage('loginMessage', 'Logged out successfully!', 'success');
}

function showDashboard() {
    const dashboard = document.getElementById('dashboard');
    if (dashboard) {
        dashboard.classList.remove('hidden');
        dashboard.scrollIntoView({ behavior: 'smooth' });
    }
}

// Dashboard functions
async function showProfile() {
    hideAllSections();
    const profileSection = document.getElementById('profileSection');
    if (profileSection) {
        profileSection.classList.remove('hidden');
    }
    
    const profileInfo = document.getElementById('profileInfo');
    if (!profileInfo) return;
    
    profileInfo.innerHTML = '<div class="loading"></div>';
    
    try {
        // Get person ID from the current user (this would need to be stored during login)
        const response = await fetch(`${REGISTRATION_API}/en/persons/2`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        
        if (response.ok) {
            const person = await response.json();
            profileInfo.innerHTML = `
                <div class="row">
                    <div class="col-md-6">
                        <h5>Personal Information</h5>
                        <p><strong>Name:</strong> ${person.firstname} ${person.lastname}</p>
                        <p><strong>Email:</strong> ${person.email}</p>
                        <p><strong>Date of Birth:</strong> ${person.date_of_birth}</p>
                        <p><strong>Role:</strong> ${person.role_id === 1 ? 'Recruiter' : 'Applicant'}</p>
                    </div>
                    <div class="col-md-6">
                        <h5>Account Information</h5>
                        <p><strong>Username:</strong> ${currentUser.username}</p>
                        <p><strong>Status:</strong> <span class="badge bg-success">Active</span></p>
                    </div>
                </div>
            `;
        } else {
            profileInfo.innerHTML = '<div class="alert alert-danger">Failed to load profile information.</div>';
        }
    } catch (error) {
        profileInfo.innerHTML = `<div class="alert alert-danger">Error loading profile: ${error.message}</div>`;
    }
}

async function showApplications() {
    hideAllSections();
    const applicationsSection = document.getElementById('applicationsSection');
    if (applicationsSection) {
        applicationsSection.classList.remove('hidden');
    }
    
    const applicationsList = document.getElementById('applicationsList');
    if (!applicationsList) return;
    
    applicationsList.innerHTML = '<div class="loading"></div>';
    
    try {
        const response = await fetch(`${JOB_API}/en/applications`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        
        if (response.ok) {
            const applications = await response.json();
            if (applications.length === 0) {
                applicationsList.innerHTML = '<div class="alert alert-info">No applications found. Create your first application!</div>';
            } else {
                let html = '<div class="table-responsive"><table class="table table-striped">';
                html += '<thead><tr><th>ID</th><th>Name</th><th>Description</th><th>Status</th><th>Actions</th></tr></thead><tbody>';
                
                applications.forEach(app => {
                    html += `
                        <tr>
                            <td>${app.id}</td>
                            <td>${app.name}</td>
                            <td>${app.description || 'N/A'}</td>
                            <td><span class="badge bg-primary">${app.status || 'Pending'}</span></td>
                            <td>
                                <button class="btn btn-sm btn-outline-primary" onclick="viewApplication(${app.id})">View</button>
                            </td>
                        </tr>
                    `;
                });
                
                html += '</tbody></table></div>';
                applicationsList.innerHTML = html;
            }
        } else {
            applicationsList.innerHTML = '<div class="alert alert-danger">Failed to load applications.</div>';
        }
    } catch (error) {
        applicationsList.innerHTML = `<div class="alert alert-danger">Error loading applications: ${error.message}</div>`;
    }
}

async function showNewApplication() {
    hideAllSections();
    const newApplicationSection = document.getElementById('newApplicationSection');
    if (newApplicationSection) {
        newApplicationSection.classList.remove('hidden');
    }
    
    // Load competences and availability options
    await loadCompetences();
    await loadAvailability();
}

async function loadCompetences() {
    const competencesSelect = document.getElementById('applicationCompetences');
    if (!competencesSelect) return;
    
    try {
        const response = await fetch(`${JOB_API}/en/competences`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        
        if (response.ok) {
            const competences = await response.json();
            competencesSelect.innerHTML = '';
            competences.forEach(comp => {
                const option = document.createElement('option');
                option.value = comp.id;
                option.textContent = comp.name;
                competencesSelect.appendChild(option);
            });
        }
    } catch (error) {
        console.error('Error loading competences:', error);
    }
}

async function loadAvailability() {
    const availabilitySelect = document.getElementById('applicationAvailability');
    if (!availabilitySelect) return;
    
    try {
        const response = await fetch(`${JOB_API}/en/availability`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        
        if (response.ok) {
            const availability = await response.json();
            availabilitySelect.innerHTML = '';
            availability.forEach(avail => {
                const option = document.createElement('option');
                option.value = avail.id;
                option.textContent = `${avail.from_date} to ${avail.to_date}`;
                availabilitySelect.appendChild(option);
            });
        }
    } catch (error) {
        console.error('Error loading availability:', error);
    }
}

async function handleApplicationSubmit(event) {
    event.preventDefault();
    
    const formData = {
        name: document.getElementById('applicationName').value,
        description: document.getElementById('applicationDescription').value,
        competences: Array.from(document.getElementById('applicationCompetences').selectedOptions).map(opt => parseInt(opt.value)),
        availability: Array.from(document.getElementById('applicationAvailability').selectedOptions).map(opt => parseInt(opt.value))
    };

    try {
        const response = await fetch(`${JOB_API}/en/applications`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify(formData)
        });

        if (response.ok) {
            alert('Application submitted successfully!');
            document.getElementById('applicationForm').reset();
            showApplications(); // Switch to applications view
        } else {
            const result = await response.json();
            alert(`Failed to submit application: ${result.detail || 'Unknown error'}`);
        }
    } catch (error) {
        alert(`Error submitting application: ${error.message}`);
    }
}

function showSettings() {
    hideAllSections();
    const settingsSection = document.getElementById('settingsSection');
    if (settingsSection) {
        settingsSection.classList.remove('hidden');
    }
}

function viewApplication(applicationId) {
    // This would open a detailed view of the application
    alert(`Viewing application ${applicationId}. This feature would show detailed application information.`);
}

// Smooth scrolling for navigation links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth'
            });
        }
    });
});

// Auto-refresh service status every 30 seconds
setInterval(checkServiceStatus, 30000); 