// Form handling and validation
document.addEventListener('DOMContentLoaded', function() {
    // Form validation for signup
    const signupForm = document.getElementById('signupForm');
    if (signupForm) {
        signupForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const email = document.querySelector('input[name="email"]').value;
            const phone = document.querySelector('input[name="phone"]').value;
            const password = document.querySelector('input[name="password"]').value;
            const confirmPassword = document.querySelector('input[name="confirm_password"]').value;
            
            // Clear any previous error messages
            clearErrorMessages();
            
            // Validation
            if (!email || !phone || !password || !confirmPassword) {
                showError('All fields are required!');
                return false;
            }
            
            if (!isValidEmail(email)) {
                showError('Please enter a valid email address!');
                return false;
            }
            
            if (password.length < 6) {
                showError('Password must be at least 6 characters long!');
                return false;
            }
            
            if (!isStrongPassword(password)) {
                showError('Password must contain at least one uppercase letter, one lowercase letter, and one number!');
                return false;
            }
            
            if (password !== confirmPassword) {
                showError('Passwords do not match!');
                return false;
            }
            
            // Show loading state
            const submitBtn = signupForm.querySelector('button[type="submit"]');
            const originalText = submitBtn.textContent;
            submitBtn.textContent = 'Creating Account...';
            submitBtn.disabled = true;
            
            // If validation passes, submit the form
            signupForm.submit();
        });
    }

    // Real-time password matching validation
    const passwordInput = document.querySelector('input[name="password"]');
    const confirmPasswordInput = document.querySelector('input[name="confirm_password"]');
    const emailInput = document.querySelector('input[name="email"]');
    
    if (passwordInput && confirmPasswordInput) {
        function validatePasswords() {
            const password = passwordInput.value;
            const confirmPassword = confirmPasswordInput.value;
            
            // Clear previous error messages
            clearErrorMessages();
            
            if (password && password.length < 6) {
                showError('Password must be at least 6 characters long!');
            } else if (password && !isStrongPassword(password)) {
                showError('Password must contain at least one uppercase letter, one lowercase letter, and one number!');
            } else if (confirmPassword && password !== confirmPassword) {
                showError('Passwords do not match!');
            }
        }
        
        // Add event listeners for real-time validation
        passwordInput.addEventListener('input', validatePasswords);
        confirmPasswordInput.addEventListener('input', validatePasswords);
    }
    
    // Real-time email validation
    if (emailInput) {
        emailInput.addEventListener('input', function() {
            const email = emailInput.value;
            clearErrorMessages();
            
            if (email && !isValidEmail(email)) {
                showError('Please enter a valid email address!');
            }
        });
    }

    // Add loading states to forms
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', function() {
            const submitBtn = this.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.textContent = 'Processing...';
                submitBtn.disabled = true;
            }
        });
    });
});
