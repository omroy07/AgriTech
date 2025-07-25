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
