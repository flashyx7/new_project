# Frontend Documentation - The Recruitment System

## Overview

The frontend of The Recruitment System is a modern, responsive web application built with HTML5, CSS3, and vanilla JavaScript. It provides a comprehensive user interface for both applicants and recruiters to interact with the microservices backend.

## Features

### 🎨 **Modern Design**
- **Responsive Layout**: Works perfectly on desktop, tablet, and mobile devices
- **Bootstrap 5**: Latest Bootstrap framework for consistent styling
- **Custom CSS**: Enhanced styling with gradients, animations, and modern UI elements
- **Font Awesome Icons**: Professional icons throughout the interface

### 🔐 **Authentication System**
- **User Registration**: Complete registration form with validation
- **User Login**: Secure login with JWT token management
- **Session Management**: Persistent login sessions using localStorage
- **Role-based Access**: Different interfaces for applicants and recruiters

### 📊 **Dashboard Features**
- **Profile Management**: View and manage personal information
- **Application Management**: Create, view, and manage job applications
- **Service Status Monitoring**: Real-time status of all microservices
- **Settings Panel**: Account and system settings (expandable)

### 🚀 **Interactive Elements**
- **Real-time Service Status**: Automatic checking of all microservices health
- **Form Validation**: Client-side and server-side validation
- **Loading States**: Visual feedback during API calls
- **Smooth Animations**: CSS transitions and animations for better UX

## File Structure

```
edge_service/
├── templates/
│   └── index.html          # Main HTML template
├── static/
│   ├── css/
│   │   └── style.css       # Custom CSS styles
│   └── js/
│       └── application.js  # Main JavaScript functionality
└── FRONTEND_README.md      # This documentation
```

## Key Components

### 1. **Navigation Bar**
- Responsive navigation with collapsible menu
- Dynamic links based on authentication status
- Brand logo with gradient text effect

### 2. **Hero Section**
- Eye-catching gradient background
- Feature cards for different user types
- Call-to-action buttons

### 3. **Service Status Section**
- Real-time monitoring of all microservices
- Color-coded status indicators
- Auto-refresh every 30 seconds

### 4. **Registration Form**
- Complete user registration with all required fields
- Role selection (Applicant/Recruiter)
- Client-side validation
- Success/error messaging

### 5. **Login Form**
- Secure authentication
- JWT token management
- Session persistence
- Dashboard redirection

### 6. **Dashboard**
- **Profile Section**: Personal information display
- **Applications Section**: Job application management
- **New Application Section**: Application creation form
- **Settings Section**: Account settings (placeholder)

## API Integration

The frontend integrates with all backend microservices through the Edge Service (API Gateway):

### **Authentication Endpoints**
- `POST /auth/login` - User login
- `POST /registration/register` - User registration
- `GET /registration/en/persons/{id}` - Get user profile

### **Job Application Endpoints**
- `GET /job-application/en/applications` - List applications
- `POST /job-application/en/applications` - Create application
- `GET /job-application/en/competences` - Get competences
- `GET /job-application/en/availability` - Get availability options

### **Service Health Endpoints**
- `GET /health` - Service health check for all microservices

## Styling Features

### **Color Scheme**
- Primary: `#667eea` (Blue gradient)
- Secondary: `#764ba2` (Purple gradient)
- Success: `#28a745` (Green)
- Danger: `#dc3545` (Red)
- Warning: `#ffc107` (Yellow)
- Info: `#17a2b8` (Cyan)

### **CSS Features**
- **CSS Variables**: Consistent color scheme
- **Gradients**: Modern gradient backgrounds
- **Animations**: Smooth transitions and hover effects
- **Responsive Design**: Mobile-first approach
- **Custom Scrollbar**: Styled scrollbar with gradients
- **Focus States**: Accessibility-friendly focus indicators

### **JavaScript Features**
- **ES6+ Syntax**: Modern JavaScript features
- **Async/Await**: Clean asynchronous code
- **Local Storage**: Session persistence
- **Error Handling**: Comprehensive error management
- **Service Monitoring**: Real-time health checks

## Browser Compatibility

- **Chrome**: 90+
- **Firefox**: 88+
- **Safari**: 14+
- **Edge**: 90+

## Performance Features

- **Lazy Loading**: Images and content loaded on demand
- **Minified Assets**: Optimized CSS and JavaScript
- **CDN Resources**: Bootstrap and Font Awesome from CDN
- **Efficient DOM**: Minimal DOM manipulation
- **Caching**: Local storage for session data

## Security Features

- **JWT Tokens**: Secure authentication
- **HTTPS Ready**: Prepared for secure connections
- **Input Validation**: Client and server-side validation
- **XSS Protection**: Sanitized user inputs
- **CSRF Protection**: Token-based protection

## Accessibility Features

- **ARIA Labels**: Screen reader support
- **Keyboard Navigation**: Full keyboard accessibility
- **Focus Indicators**: Clear focus states
- **Color Contrast**: WCAG compliant color ratios
- **Semantic HTML**: Proper HTML structure

## Usage Instructions

### **For Applicants**
1. Visit the homepage
2. Click "Get Started" or navigate to Registration
3. Fill out the registration form
4. Login with your credentials
5. Access the dashboard to create job applications

### **For Recruiters**
1. Visit the homepage
2. Click "Access Dashboard" or navigate to Login
3. Login with recruiter credentials
4. Access the dashboard to manage applications

### **Service Monitoring**
- The service status section automatically updates every 30 seconds
- Green indicators show healthy services
- Red indicators show service issues

## Development

### **Local Development**
1. Start all backend services
2. Access the frontend at `http://localhost:8080`
3. The frontend will automatically connect to backend services

### **Customization**
- Modify `static/css/style.css` for styling changes
- Update `static/js/application.js` for functionality changes
- Edit `templates/index.html` for structure changes

### **Adding New Features**
1. Add HTML structure in `index.html`
2. Add CSS styles in `style.css`
3. Add JavaScript functionality in `application.js`
4. Test across different devices and browsers

## Troubleshooting

### **Common Issues**

1. **Services Not Loading**
   - Check if all backend services are running
   - Verify service URLs in `application.js`
   - Check browser console for errors

2. **Login Issues**
   - Verify username and password
   - Check if user exists in database
   - Clear browser cache and localStorage

3. **Styling Issues**
   - Ensure CSS file is loading correctly
   - Check for CSS conflicts
   - Verify Bootstrap is loading

4. **API Errors**
   - Check network connectivity
   - Verify API endpoints are correct
   - Check browser console for detailed errors

## Future Enhancements

### **Planned Features**
- **Real-time Notifications**: WebSocket integration
- **File Upload**: Resume and document upload
- **Advanced Search**: Job and application search
- **Email Integration**: Email notifications
- **Mobile App**: React Native mobile application

### **Technical Improvements**
- **Progressive Web App**: PWA capabilities
- **Service Worker**: Offline functionality
- **Performance Optimization**: Code splitting and lazy loading
- **Internationalization**: Multi-language support
- **Advanced Analytics**: User behavior tracking

## Contributing

When contributing to the frontend:

1. Follow the existing code style
2. Test on multiple browsers and devices
3. Ensure accessibility compliance
4. Update documentation for new features
5. Add appropriate error handling

## License

This frontend is part of The Recruitment System and follows the same license as the main project. 