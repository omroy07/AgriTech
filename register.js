// Password toggle functionality
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

// Role icon update
function updateRoleIcon() {
  const roleSelect = document.getElementById("role");
  const roleIcon = document.getElementById("role-icon");
  const value = roleSelect.value;

  roleIcon.className = "fas fa-user-tag";

  switch (value) {
    case "buyer":
      roleIcon.className = "fas fa-shopping-cart role-buyer";
      break;
    case "farmer":
      roleIcon.className = "fas fa-tractor role-farmer";
      break;
    case "equipment":
      roleIcon.className = "fas fa-tools role-equipment";
      break;
    case "grocery":
      roleIcon.className = "fas fa-store role-grocery";
      break;
    default:
      roleIcon.className = "fas fa-user-tag";
  }
}

// Password strength checker
function checkPasswordStrength() {
  const password = document.getElementById("password").value;
  const strengthBar = document.getElementById("strength-bar");
  const strengthText = document.getElementById("strength-text");

  let strength = 0;
  let feedback = "";

  // Length check
  if (password.length >= 8) strength += 25;

  if (/[a-z]/.test(password)) strength += 25;

  if (/[A-Z]/.test(password)) strength += 25;
  
  if (/[\d\W]/.test(password)) strength += 25;

  // Update strength bar
  strengthBar.className = "strength-bar";

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

// Form progress tracking
function updateProgress() {
  const fields = ["role", "fullname", "email", "password"];
  let completedFields = 0;

  fields.forEach((fieldId, index) => {
    const field = document.getElementById(fieldId);
    const step = document.getElementById(`step-${index + 1}`);

    if (field.value.trim() !== "") {
      step.classList.add("completed");
      completedFields++;
    } else {
      step.classList.remove("completed");
    }
  });

  const password = document.getElementById("password").value;
  const finalStep = document.getElementById("step-5");

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

// Enhanced register handler
function handleRegister(event) {
  event.preventDefault();

  const registerBtn = document.getElementById("register-btn");
  const registerText = document.getElementById("register-text");
  const inputs = document.querySelectorAll("input, select");

  registerBtn.classList.add("loading");
  registerText.textContent = "Creating Account...";
  registerBtn.disabled = true;

  inputs.forEach((input) => {
    input.classList.remove("error", "success");
  });

  const formData = {
    role: document.getElementById("role").value,
    fullname: document.getElementById("fullname").value.trim(),
    email: document.getElementById("email").value.trim(),
    password: document.getElementById("password").value
  };
  setTimeout(() => {
    const result = window.authManager.register(formData);
    
    if (result.success) {
      inputs.forEach((input) => {
        input.classList.add("success");
      });
      
      registerText.textContent = "Account Created!";
      showAuthMessage(result.message, 'success');
      setTimeout(() => {
        window.location.href = "main.html";
      }, 1500);
    } else {
      // Show error message
      showAuthMessage(result.message, 'error');
      
      // Mark relevant fields as error
      if (result.message.includes('email')) {
        document.getElementById("email").classList.add("error");
      }
      if (result.message.includes('password') || result.message.includes('Password')) {
        document.getElementById("password").classList.add("error");
      }
      
      registerBtn.classList.remove("loading");
      registerText.textContent = "Create Account";
      registerBtn.disabled = false;
    }
  }, 2000);
}

// Add input event listeners for progress tracking
document.querySelectorAll("input, select").forEach((input) => {
  input.addEventListener("input", updateProgress);
  input.addEventListener("change", updateProgress);

  input.addEventListener("focus", function () {
    this.parentElement.style.transform = "translateY(-2px)";
  });

  input.addEventListener("blur", function () {
    this.parentElement.style.transform = "translateY(0)";
  });
});

// Keyboard navigation
document.addEventListener("keydown", function (e) {
  if (e.key === "Enter") {
    const form = document.querySelector("form");
    if (
      document.activeElement.tagName === "INPUT" ||
      document.activeElement.tagName === "SELECT"
    ) {
      const inputs = Array.from(form.querySelectorAll("input, select"));
      const currentIndex = inputs.indexOf(document.activeElement);
      if (currentIndex < inputs.length - 1) {
        inputs[currentIndex + 1].focus();
      } else {
        form.dispatchEvent(new Event("submit"));
      }
    }
  }
});

document.addEventListener("DOMContentLoaded", updateProgress);
