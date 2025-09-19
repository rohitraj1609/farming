// Form validation functions
// Enhanced password validation functions
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

function isStrongPassword(password) {
    // At least 6 characters, one uppercase, one lowercase, one number
    const hasUpperCase = /[A-Z]/.test(password);
    const hasLowerCase = /[a-z]/.test(password);
    const hasNumbers = /\d/.test(password);
    const hasMinimumLength = password.length >= 6;
    
    return hasUpperCase && hasLowerCase && hasNumbers && hasMinimumLength;
}

// Function to show error messages
function showError(message) {
    // Remove any existing error messages
    clearErrorMessages();
    
    // Create error message element
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.style.cssText = 'color: #dc3545; background-color: #f8d7da; border: 1px solid #f5c6cb; padding: 10px; margin: 10px 0; border-radius: 4px; text-align: center;';
    errorDiv.textContent = message;
    
    // Insert error message after the form
    const signupForm = document.getElementById('signupForm');
    if (signupForm) {
        signupForm.parentNode.insertBefore(errorDiv, signupForm.nextSibling);
    }
}

// Function to clear error messages
function clearErrorMessages() {
    const existingErrors = document.querySelectorAll('.error-message');
    existingErrors.forEach(error => error.remove());
}

// Function to show success messages
function showSuccess(message) {
    // Remove any existing messages
    clearErrorMessages();
    clearSuccessMessages();
    
    // Create success message element
    const successDiv = document.createElement('div');
    successDiv.className = 'success-message';
    successDiv.style.cssText = 'color: #155724; background-color: #d4edda; border: 1px solid #c3e6cb; padding: 10px; margin: 10px 0; border-radius: 4px; text-align: center; font-weight: bold;';
    successDiv.textContent = message;
    
    // Insert success message after the form
    const signupForm = document.getElementById('signupForm');
    if (signupForm) {
        signupForm.parentNode.insertBefore(successDiv, signupForm.nextSibling);
    }
}

// Function to clear success messages
function clearSuccessMessages() {
    const existingSuccess = document.querySelectorAll('.success-message');
    existingSuccess.forEach(success => success.remove());
}
