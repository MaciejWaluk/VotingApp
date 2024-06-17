document.getElementById('registrationForm').addEventListener('submit', function(event) {
    let isValid = true;
    let email = document.getElementById('id_email');
    let pesel = document.getElementById('id_nr_pesel');
    let password1 = document.getElementById('id_password1');
    let password2 = document.getElementById('id_password2');

    let emailErrors = document.getElementById('emailErrors');
    let peselErrors = document.getElementById('peselErrors');
    let password1Errors = document.getElementById('password1Errors');
    let password2Errors = document.getElementById('password2Errors');

    emailErrors.textContent = '';
    peselErrors.textContent = '';
    password1Errors.textContent = '';
    password2Errors.textContent = '';


    // Email validation
     if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.value)) {
        emailErrors.textContent = 'Enter a valid email address.';
        isValid = false;
    }

    // PESEL validation
     if (!/^\d{11}$/.test(pesel.value)) {
        peselErrors.textContent = 'Pesel number must be exactly 11 digits.';
        isValid = false;
    }

    // Password validation
     if (password1.value.length < 8) {
        password1Errors.textContent = 'Password must be at least 8 characters long.';
        isValid = false;
    }

     if (password1.value !== password2.value) {
        password2Errors.textContent = 'Passwords do not match.';
        isValid = false;
    }

    if (!isValid) {
        event.preventDefault();
    }
});
