function handleRegister(event) {
	event.preventDefault();
	alert("Registration Successful! Redirecting to Login...");
	window.location.href = "login.html";
}

function handleLogin(event) {
	event.preventDefault();
	alert("Login Successful! Redirecting to Dashboard...");
	window.location.href = "main.html";
}

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
