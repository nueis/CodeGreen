document.addEventListener("DOMContentLoaded", function() {
    // Error messages initially hidden
    document.querySelectorAll(".error-msg").forEach(function(element) {
        element.style.display = "none";
    });

    // Domain select change event listener
    document.getElementById('domain-select').addEventListener('change', function() {
        const customDomainInput = document.getElementById('custom-domain');
        if (this.value === 'custom') {
            customDomainInput.style.display = 'inline-block';
            this.style.display = 'none';
        } else {
            customDomainInput.style.display = 'none';
        }
    });

    // Form validation example for showing error messages
    document.getElementById('signup-form').addEventListener('submit', function(event) {
        let hasError = false;

        // User ID validation
        const userId = document.getElementById('user-id').value;
        if (userId === "") {
            document.getElementById('user-id-error').style.display = "block";
            hasError = true;
        } else {
            document.getElementById('user-id-error').style.display = "none";
        }

        // Password validation
        const password = document.getElementById('password').value;
        if (password === "") {
            document.getElementById('password-error').style.display = "block";
            hasError = true;
        } else {
            document.getElementById('password-error').style.display = "none";
        }

        // Confirm Password validation
        const confirmPassword = document.getElementById('confirm-password').value;
        if (confirmPassword !== password) {
            document.getElementById('confirm-password-error').style.display = "block";
            hasError = true;
        } else {
            document.getElementById('confirm-password-error').style.display = "none";
        }

        // Nickname validation
        const nickname = document.getElementById('nickname').value;
        if (nickname === "") {
            document.getElementById('nickname-error').style.display = "block";
            hasError = true;
        } else {
            document.getElementById('nickname-error').style.display = "none";
        }

        if (hasError) {
            event.preventDefault();
        }
    });
});