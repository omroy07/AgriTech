// login.js — AgriTech Login Page Handler
// Only change from original: handleLogin is now async (Firebase calls are async)

async function handleLogin(event) {
  event.preventDefault();

  const emailInput = document.getElementById("email");
  const passwordInput = document.getElementById("password");
  const loginBtn = document.querySelector('button[type="submit"]');

  const email    = emailInput.value.trim();
  const password = passwordInput.value;

  if (!email || !password) {
    showAuthMessage("Please enter both email and password", "error");
    return;
  }

  // Loading state
  const originalText = loginBtn.innerText;
  loginBtn.innerText  = "Logging in...";
  loginBtn.disabled   = true;

  // Clear previous error styles
  emailInput.classList.remove("error");
  passwordInput.classList.remove("error");

  const result = await window.authManager.login(email, password);

  if (result.success) {
    showAuthMessage(result.message, "success");
    // Role-based redirect
    setTimeout(() => {
      window.location.href = window.authManager.getHomePageForRole(result.user.role);
    }, 1000);
  } else {
    showAuthMessage(result.message, "error");

    const msg = result.message.toLowerCase();
    if (msg.includes("email")) {
      emailInput.classList.add("error");
    } else {
      passwordInput.classList.add("error");
    }

    loginBtn.innerText = originalText;
    loginBtn.disabled  = false;
  }
}

// Remove error styling on input
document.querySelectorAll("input").forEach((input) => {
  input.addEventListener("input", () => input.classList.remove("error"));
});

function togglePassword() {
  const passwordInput = document.getElementById("password");
  const eyeIcon = document.getElementById("password-eye");
  if (passwordInput.type === "password") {
    passwordInput.type = "text";
    eyeIcon.className  = "fas fa-eye-slash";
  } else {
    passwordInput.type = "password";
    eyeIcon.className  = "fas fa-eye";
  }
}
