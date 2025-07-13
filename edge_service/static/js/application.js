
/**
 * Recruitment System - Frontend JavaScript
 * Only includes functionality for implemented features
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('Recruitment System Frontend Loaded');

    // Initialize tooltips if Bootstrap is loaded
    if (typeof bootstrap !== 'undefined') {
        var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }

    // Initialize forms
    initializeForms();
    
    // Initialize login form
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', handleLogin);
    }

    // Initialize registration form
    const registrationForm = document.getElementById('registrationForm');
    if (registrationForm) {
        registrationForm.addEventListener('submit', handleRegistration);
    }
});

function initializeForms() {
    // Form validation
    const forms = document.querySelectorAll('.needs-validation');
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });
}

function handleLogin(event) {
    event.preventDefault();
    
    const form = event.target;
    const username = document.getElementById('loginUsername').value;
    const password = document.getElementById('loginPassword').value;

    if (!username.trim() || !password.trim()) {
        showAlert('Please enter both username and password.', 'warning');
        return false;
    }

    // Show loading state
    const submitBtn = form.querySelector('button[type="submit"]');
    const spinner = document.getElementById('loginSpinner');
    const buttonText = document.getElementById('loginText');
    
    if (submitBtn && spinner && buttonText) {
        submitBtn.disabled = true;
        spinner.style.display = 'inline-block';
        buttonText.textContent = 'Logging in...';
    }

    // Send login request
    const loginData = {
        username: username,
        password: password
    };

    fetch('/auth/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(loginData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.token) {
            // Store token and redirect
            localStorage.setItem('authToken', data.token);
            showAlert('Login successful! Redirecting...', 'success');
            setTimeout(() => {
                window.location.href = '/dashboard';
            }, 1000);
        } else {
            showAlert('Login failed. Please check your credentials.', 'danger');
        }
    })
    .catch(error => {
        console.error('Login error:', error);
        showAlert('Login failed. Please try again.', 'danger');
    })
    .finally(() => {
        // Reset button state
        if (submitBtn && spinner && buttonText) {
            submitBtn.disabled = false;
            spinner.style.display = 'none';
            buttonText.textContent = 'Login';
        }
    });

    return false;
}

function handleRegistration(event) {
    event.preventDefault();
    
    const form = event.target;
    
    // Get form values
    const firstName = document.getElementById('firstName').value;
    const lastName = document.getElementById('lastName').value;
    const email = document.getElementById('email').value;
    const dateOfBirth = document.getElementById('dateOfBirth').value;
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirmPassword').value;
    const role = document.getElementById('role').value;

    // Validate passwords match
    if (password !== confirmPassword) {
        showAlert('Passwords do not match.', 'danger');
        return false;
    }

    // Show loading state
    const submitBtn = form.querySelector('button[type="submit"]');
    const spinner = document.getElementById('registerSpinner');
    const buttonText = document.getElementById('registerText');
    
    if (submitBtn && spinner && buttonText) {
        submitBtn.disabled = true;
        spinner.style.display = 'inline-block';
        buttonText.textContent = 'Creating Account...';
    }

    // Prepare registration data
    const registrationData = {
        firstname: firstName,
        lastname: lastName,
        email: email,
        date_of_birth: dateOfBirth,
        username: username,
        password: password,
        role_id: parseInt(role)
    };

    // Send registration request
    fetch('/registration/register', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(registrationData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            showAlert('Registration successful! You can now login.', 'success');
            setTimeout(() => {
                window.location.href = '/login';
            }, 2000);
        } else {
            showAlert(data.message || 'Registration failed. Please try again.', 'danger');
        }
    })
    .catch(error => {
        console.error('Registration error:', error);
        showAlert('Registration failed. Please try again.', 'danger');
    })
    .finally(() => {
        // Reset button state
        if (submitBtn && spinner && buttonText) {
            submitBtn.disabled = false;
            spinner.style.display = 'none';
            buttonText.textContent = 'Create Account';
        }
    });

    return false;
}

function showAlert(message, type) {
    // Try to find existing message containers
    let messageContainer = document.getElementById('loginMessage') || 
                          document.getElementById('registrationMessage') ||
                          document.getElementById('messageContainer');
    
    if (!messageContainer) {
        // Create a temporary message container
        messageContainer = document.createElement('div');
        messageContainer.id = 'messageContainer';
        messageContainer.className = 'mt-3';
        
        // Try to insert after form or at the beginning of container
        const form = document.querySelector('form');
        if (form && form.parentNode) {
            form.parentNode.insertBefore(messageContainer, form.nextSibling);
        } else {
            const container = document.querySelector('.container') || document.body;
            container.insertBefore(messageContainer, container.firstChild);
        }
    }

    // Create alert HTML
    const alertHtml = `
        <div class="alert alert-${type} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>
    `;

    messageContainer.innerHTML = alertHtml;

    // Auto-dismiss after 5 seconds for success messages
    if (type === 'success') {
        setTimeout(() => {
            const alert = messageContainer.querySelector('.alert');
            if (alert) {
                alert.remove();
            }
        }, 5000);
    }
}

// Check if user is authenticated
function checkAuth() {
    const token = localStorage.getItem('authToken');
    if (token) {
        // Verify token with backend
        fetch('/auth/verify', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({token: token})
        })
        .then(response => response.json())
        .then(data => {
            if (!data.valid) {
                localStorage.removeItem('authToken');
                window.location.href = '/login';
            }
        })
        .catch(error => {
            console.error('Auth check error:', error);
            localStorage.removeItem('authToken');
        });
    }
}

// Logout function
function logout() {
    localStorage.removeItem('authToken');
    window.location.href = '/login';
}

// Show job details
function showJobDetails(jobType) {
    const jobDetails = {
        'frontend': {
            title: 'Frontend Developer',
            company: 'Tech Innovations Inc.',
            description: 'We are looking for a skilled Frontend Developer to join our team and help build amazing user experiences. You will work with modern technologies and collaborate with designers and backend developers.',
            requirements: ['3+ years of React experience', 'Strong JavaScript skills', 'CSS and HTML expertise', 'Experience with modern build tools']
        },
        'backend': {
            title: 'Backend Developer',
            company: 'Digital Solutions Ltd.',
            description: 'Join our backend team to develop scalable APIs and robust server-side applications. You will be responsible for designing and implementing server-side logic.',
            requirements: ['Python and FastAPI experience', 'Database design skills', 'API development expertise', 'Knowledge of cloud platforms']
        },
        'designer': {
            title: 'UI/UX Designer',
            company: 'Creative Agency Co.',
            description: 'We need a creative UI/UX Designer to create beautiful and intuitive user interfaces. You will work closely with product managers and developers.',
            requirements: ['Figma and Sketch proficiency', 'User research experience', 'Prototyping skills', 'Portfolio of design work']
        },
        'devops': {
            title: 'DevOps Engineer',
            company: 'Cloud Systems Inc.',
            description: 'Help us build and maintain our cloud infrastructure and deployment pipelines. You will be responsible for CI/CD, monitoring, and automation.',
            requirements: ['AWS/Azure experience', 'Docker and Kubernetes', 'CI/CD pipeline setup', 'Infrastructure as Code']
        },
        'product': {
            title: 'Product Manager',
            company: 'StartupXYZ',
            description: 'Lead product strategy and development for our growing technology platform. You will work with engineering, design, and marketing teams.',
            requirements: ['Product management experience', 'Agile methodology', 'Data analysis skills', 'Strong communication skills']
        },
        'datascience': {
            title: 'Data Scientist',
            company: 'AI Innovations Corp.',
            description: 'Join our data science team to extract insights from large datasets and build ML models. You will work on cutting-edge AI projects.',
            requirements: ['Python and R proficiency', 'Machine learning expertise', 'Statistical analysis skills', 'Experience with big data tools']
        }
    };

    const job = jobDetails[jobType];
    if (job) {
        const requirementsList = job.requirements.map(req => `<li>${req}</li>`).join('');
        
        showAlert(`
            <strong>${job.title}</strong> at ${job.company}<br><br>
            <strong>Description:</strong><br>
            ${job.description}<br><br>
            <strong>Requirements:</strong>
            <ul>${requirementsList}</ul>
            <em>Note: This is a demo listing. Application functionality is not yet implemented.</em>
        `, 'info');
    }
}
