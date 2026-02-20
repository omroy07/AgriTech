// register.js — AgriTech Registration Page Handler
// Change from original: handleRegister is async + removed fake setTimeout

function togglePassword() {
  const passwordInput = document.getElementById("password");
  const eyeIcon       = document.getElementById("password-eye");
  if (passwordInput.type === "password") {
    passwordInput.type = "text";
    eyeIcon.className  = "fas fa-eye-slash";
  } else {
    passwordInput.type = "password";
    eyeIcon.className  = "fas fa-eye";
  }
}

function handleBack() {
  if (window.history.length > 1) {
    window.history.back();
  } else {
    window.location.href = "index.html";
  }
}

function updateRoleIcon() {
  const roleSelect = document.getElementById("role");
  const roleIcon   = document.getElementById("role-icon");
  const value      = roleSelect.value;

  const iconMap = {
    buyer:     "fas fa-shopping-cart role-buyer",
    farmer:    "fas fa-tractor role-farmer",
    equipment: "fas fa-tools role-equipment",
    grocery:   "fas fa-store role-grocery",
    expert:    "fas fa-user-graduate role-expert",
  };
  roleIcon.className = iconMap[value] || "fas fa-user-tag";
}

function checkPasswordStrength() {
  const password     = document.getElementById("password").value;
  const strengthBar  = document.getElementById("strength-bar");
  const strengthText = document.getElementById("strength-text");

  let strength = 0;
  if (password.length >= 8)       strength += 25;
  if (/[a-z]/.test(password))     strength += 25;
  if (/[A-Z]/.test(password))     strength += 25;
  if (/[\d\W]/.test(password))    strength += 25;

  strengthBar.className = "strength-bar";
  let feedback = "";

  if (strength <= 25) {
    strengthBar.classList.add("strength-weak");
    feedback = "Weak password";
  } else if (strength <= 50) {
    strengthBar.classList.add("strength-fair");
    feedback = "Fair password";
  } else if (strength <= 75) {
    strengthBar.classList.add("strength-good");
    feedback = "Good password";
  } else {
    strengthBar.classList.add("strength-strong");
    feedback = "Strong password";
  }

  strengthText.textContent = password.length > 0 ? feedback : "";
}

function updateProgress() {
  const fields = ["role", "fullname", "email", "password"];
  fields.forEach((fieldId, index) => {
    const field = document.getElementById(fieldId);
    const step  = document.getElementById(`step-${index + 1}`);
    if (field && field.value.trim() !== "") {
      step.classList.add("completed");
    } else if (step) {
      step.classList.remove("completed");
    }
  });

  const password  = document.getElementById("password").value;
  const finalStep = document.getElementById("step-5");
  if (finalStep) {
    if (
      password.length >= 8 &&
      /[a-z]/.test(password) &&
      /[A-Z]/.test(password) &&
      /[\d\W]/.test(password)
    ) {
      finalStep.classList.add("completed");
    } else {
      finalStep.classList.remove("completed");
    }
  }
}

// ── Main register handler (now async) ────────────────────────────────────────
async function handleRegister(event) {
  event.preventDefault();

  const registerBtn  = document.getElementById("register-btn");
  const registerText = document.getElementById("register-text");
  const inputs       = document.querySelectorAll("input, select");

  registerBtn.classList.add("loading");
  registerText.textContent = "Creating Account...";
  registerBtn.disabled     = true;

  inputs.forEach((input) => input.classList.remove("error", "success"));

  const formData = {
    role:      document.getElementById("role").value,
    fullname:  document.getElementById("fullname").value.trim(),
    email:     document.getElementById("email").value.trim(),
    password:  document.getElementById("password").value,
  };

  const result = await window.authManager.register(formData);

  if (result.success) {
    inputs.forEach((input) => input.classList.add("success"));
    registerText.textContent = "Account Created!";
    showAuthMessage(result.message, "success");
    setTimeout(() => {
      // Redirect to the role-specific home page
      window.location.href = window.authManager.getHomePageForRole(result.user.role);
    }, 1500);
  } else {
    showAuthMessage(result.message, "error");

    const msg = result.message.toLowerCase();
    if (msg.includes("email"))    document.getElementById("email").classList.add("error");
    if (msg.includes("password")) document.getElementById("password").classList.add("error");

    registerBtn.classList.remove("loading");
    registerText.textContent = "Create Account";
    registerBtn.disabled     = false;
  }
}

// Input listeners
document.querySelectorAll("input, select").forEach((input) => {
  input.addEventListener("input",  updateProgress);
  input.addEventListener("change", updateProgress);
  input.addEventListener("focus",  function () { this.parentElement.style.transform = "translateY(-2px)"; });
  input.addEventListener("blur",   function () { this.parentElement.style.transform = "translateY(0)"; });
});

document.addEventListener("keydown", function (e) {
  if (e.key === "Enter") {
    const form = document.querySelector("form");
    if (
      document.activeElement.tagName === "INPUT" ||
      document.activeElement.tagName === "SELECT"
    ) {
      const inputs = Array.from(form.querySelectorAll("input, select"));
      const idx    = inputs.indexOf(document.activeElement);
      if (idx < inputs.length - 1) {
        inputs[idx + 1].focus();
      } else {
        form.dispatchEvent(new Event("submit"));
      }
    }
  }
});

document.addEventListener("DOMContentLoaded", updateProgress);
