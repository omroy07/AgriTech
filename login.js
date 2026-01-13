function handleRegister(event) {
	event.preventDefault();
	alert("Registration Successful! Redirecting to Login...");
	window.location.href = "login.html";
}

// Login handler
function handleLogin(event) {
	event.preventDefault();

	const emailInput = document.getElementById('email');
	const passwordInput = document.getElementById('password');
	const loginBtn = document.querySelector('button[type="submit"]');

	const email = emailInput.value.trim();
	const password = passwordInput.value;

	if (!email || !password) {
		showAuthMessage('Please enter both email and password', 'error');
		return;
	}

	// Add loading state
	const originalBtnText = loginBtn.innerText;
	loginBtn.innerText = 'Logging in...';
	loginBtn.disabled = true;

	// Simulate network delay for better UX
	setTimeout(() => {
		const result = window.authManager.login(email, password);

		if (result.success) {
			showAuthMessage(result.message, 'success');

			// Redirect to main page after short delay
			setTimeout(() => {
				window.location.href = 'main.html';
			}, 1000);
		} else {
			showAuthMessage(result.message, 'error');

			// Reset button
			loginBtn.innerText = originalBtnText;
			loginBtn.disabled = false;

			// Highlight error fields
			if (result.message.toLowerCase().includes('email')) {
				emailInput.classList.add('error');
			} else {
				passwordInput.classList.add('error');
			}
		}
	}, 1000);
}

// Remove error styling on input
document.querySelectorAll('input').forEach(input => {
	input.addEventListener('input', () => {
		input.classList.remove('error');
	});
});

function togglePassword() {
	const passwordInput = document.getElementById("password");
	const eyeIcon = document.getElementById("password-eye");

	if (passwordInput.type === "password") {
		passwordInput.type = "text";
		eyeIcon.className = "fas fa-eye-slash";
	} else {
		passwordInput.type = "password";
		eyeIcon.className = "fas fa-eye";
	}
}
