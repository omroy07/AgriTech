function showLoading(show = true) {
  const loadingEl = document.getElementById("loadingIndicator");
  const formEl = document.getElementById("yieldForm");
  const resultEl = document.getElementById("resultCard");

  if (show) {
    loadingEl.style.display = "flex";
    resultEl.style.display = "none";
    formEl.style.opacity = "0.7";
    formEl.style.pointerEvents = "none";
  } else {
    loadingEl.style.display = "none";
    formEl.style.opacity = "1";
    formEl.style.pointerEvents = "auto";
  }
}

// Show result with prediction
function showPrediction(data) {
  const resultEl = document.getElementById("resultCard");
  const predictionEl = document.getElementById("predictionValue");
  const efficiencyEl = document.getElementById("efficiency");
  const efficiencyNoteEl = document.getElementById("efficiency-note");
  const rainfallImpactEl = document.getElementById("rainfall-impact");
  const rainfallNoteEl = document.getElementById("rainfall-note");
  const recommendationEl = document.getElementById("recommendation");
  const seasonTipEl = document.getElementById("season-tip");

  predictionEl.textContent = data.prediction;

  efficiencyEl.textContent = data.context.efficiency;
  efficiencyNoteEl.textContent = data.context.efficiency_note;
  rainfallImpactEl.textContent = data.context.rainfall_impact || "N/A";
  rainfallNoteEl.textContent =
    data.context.rainfall_note || "No rainfall data available.";
  recommendationEl.textContent = data.context.recommendation;

  if (data.context.season_tip) {
    seasonTipEl.textContent = data.context.season_tip;
    document.getElementById("season-tip-container").style.display = "block";
  } else {
    document.getElementById("season-tip-container").style.display = "none";
  }

  resultEl.style.display = "block";

  setTimeout(() => {
    resultEl.scrollIntoView({ behavior: "smooth", block: "start" });
  }, 100);
}

// Show form errors
function showFormErrors(errors) {
  document.querySelectorAll(".form-group").forEach((group) => {
    group.classList.remove("error", "success");
    const errorEl = group.querySelector(".error-message");
    if (errorEl) {
      errorEl.textContent = "";
    }
  });

  // Show new errors
  Object.entries(errors).forEach(([field, message]) => {
    const input = document.querySelector(`[name="${field}"]`);
    if (!input) return;

    const formGroup = input.closest(".form-group");
    if (!formGroup) return;

    formGroup.classList.add("error");

    let errorEl = formGroup.querySelector(".error-message");
    if (!errorEl) {
      errorEl = document.createElement("div");
      errorEl.className = "error-message";
      input.insertAdjacentElement("afterend", errorEl);
    }

    errorEl.textContent = message;

    // Focus the first invalid field
    if (Object.keys(errors)[0] === field) {
      setTimeout(() => {
        input.focus({ preventScroll: true });
        input.scrollIntoView({
          behavior: "smooth",
          block: "center",
          inline: "nearest",
        });
      }, 100);
    }
  });
}

// Handle form submission
document
  .getElementById("yieldForm")
  .addEventListener("submit", async function (event) {
    event.preventDefault();

    const form = event.target;

    if (!validateForm(form)) {
      return false;
    }

    const submitButton = form.querySelector('button[type="submit"]');
    const originalButtonText = submitButton.innerHTML;
    submitButton.disabled = true;
    submitButton.innerHTML =
      '<i class="fas fa-spinner fa-spin"></i> Processing...';

    showLoading(true);

    try {
      const formData = new FormData(form);

      const csrfToken = document.querySelector(
        'meta[name="csrf-token"]'
      )?.content;
      const headers = {};
      if (csrfToken) {
        headers["X-CSRFToken"] = csrfToken;
      }

      // Make API request
      const response = await fetch("/predict", {
        method: "POST",
        body: formData,
        headers: headers,
      });

      // Handle response
      const result = await response.json();

      if (!response.ok) {
        throw new Error(result.error || "Failed to get prediction");
      }

      if (result.success) {
        markFormFieldsAsValid(form);
        showPrediction(result);
        setTimeout(() => {
          document.getElementById("resultCard").scrollIntoView({
            behavior: "smooth",
            block: "start",
          });
        }, 100);
      } else if (result.errors) {
        showFormErrors(result.errors);
      } else {
        throw new Error("Invalid response from server");
      }
    } catch (error) {
      console.error("Prediction error:", error);
      showError(
        error.message ||
          "An error occurred while processing your request. Please try again."
      );
    } finally {
      submitButton.disabled = false;
      submitButton.innerHTML = originalButtonText;
      showLoading(false);
    }

    return false;
  });

// Mark all form fields as valid
function markFormFieldsAsValid(form) {
  const inputs = form.querySelectorAll("input, select");
  inputs.forEach((input) => {
    const formGroup = input.closest(".form-group");
    if (formGroup) {
      formGroup.classList.remove("error");
      formGroup.classList.add("success");
      const errorEl = formGroup.querySelector(".error-message");
      if (errorEl) {
        errorEl.textContent = "";
      }
    }
  });
}

// Client-side form validation
function validateForm(form) {
  let isValid = true;
  const errors = {};
  const currentYear = new Date().getFullYear();

  // Validation rules for each field
  const validationRules = {
    crop: {
      required: true,
      message: "Please select a crop type",
    },
    year: {
      required: true,
      number: true,
      min: 1997,
      max: currentYear + 5,
      message: `Year must be between 1997 and ${currentYear + 5}`,
    },
    season: {
      required: true,
      message: "Please select a season",
    },
    state: {
      required: true,
      message: "Please select a state",
    },
    area: {
      required: true,
      number: true,
      min: 0.01,
      message: "Area must be greater than 0",
    },
    production: {
      required: true,
      number: true,
      min: 0.01,
      message: "Production must be greater than 0",
    },
    rainfall: {
      required: true,
      number: true,
      min: 0,
      message: "Rainfall must be 0 or greater",
    },
  };

  // Validate each field against its rules
  Object.entries(validationRules).forEach(([field, rules]) => {
    const input = form.querySelector(`[name="${field}"]`);
    if (!input) return;

    const value = input.value.trim();
    const formGroup = input.closest(".form-group");

    if (formGroup) {
      formGroup.classList.remove("error", "success");
      const errorEl = formGroup.querySelector(".error-message");
      if (errorEl) errorEl.textContent = "";
    }

    if (input.disabled) return;

    if (rules.required && !value) {
      errors[field] = rules.message || "This field is required";
      return;
    }

    if (!value) return;

    if (rules.number) {
      const numValue = parseFloat(value);
      if (isNaN(numValue)) {
        errors[field] = "Please enter a valid number";
        return;
      }

      // Check min value
      if (typeof rules.min !== "undefined" && numValue < rules.min) {
        errors[field] = rules.message || `Value must be at least ${rules.min}`;
        return;
      }

      // Check max value
      if (typeof rules.max !== "undefined" && numValue > rules.max) {
        errors[field] = rules.message || `Value cannot exceed ${rules.max}`;
        return;
      }
    }
  });

  // Show errors if any
  if (Object.keys(errors).length > 0) {
    showFormErrors(errors);
    isValid = false;
  }

  return isValid;
}

// Show notification to user
function showNotification(message, type = "error") {
  let notification = document.getElementById("notification");

  if (!notification) {
    notification = document.createElement("div");
    notification.id = "notification";
    notification.className = `notification ${type}`;
    notification.role = "alert";
    notification.ariaLive = "assertive";

    // Add close button
    const closeButton = document.createElement("button");
    closeButton.className = "notification-close";
    closeButton.innerHTML = "&times;";
    closeButton.setAttribute("aria-label", "Close notification");
    closeButton.addEventListener("click", () => {
      hideNotification();
    });

    const messageEl = document.createElement("div");
    messageEl.className = "notification-message";

    notification.appendChild(messageEl);
    notification.appendChild(closeButton);
    document.body.appendChild(notification);
  }

  // Update notification content and show
  const messageEl = notification.querySelector(".notification-message");
  messageEl.textContent = message;
  notification.className = `notification ${type} show`;

  // Auto-hide after 5 seconds
  clearTimeout(notification.timeout);
  notification.timeout = setTimeout(() => {
    hideNotification();
  }, 5000);
}

// Hide notification
function hideNotification() {
  const notification = document.getElementById("notification");
  if (notification) {
    notification.classList.remove("show");
    setTimeout(() => {
      if (notification && notification.parentNode) {
        notification.parentNode.removeChild(notification);
      }
    }, 300);
  }
}

function showError(message) {
  showNotification(message, "error");
}

function showSuccess(message) {
  showNotification(message, "success");
}

// Clear validation on input
document.querySelectorAll("input, select").forEach((input) => {
  input.addEventListener("input", function () {
    this.classList.remove("error");
    const errorEl =
      this.closest(".form-group")?.querySelector(".error-message");
    if (errorEl) {
      errorEl.textContent = "";
    }
  });
});

// Initialize form
document.addEventListener("DOMContentLoaded", function () {
  const yearInput = document.getElementById("year");
  if (yearInput && !yearInput.value) {
    const currentYear = new Date().getFullYear();
    yearInput.value = currentYear;
  }

  // Add form field validation
  document.querySelectorAll('input[type="number"]').forEach((input) => {
    input.addEventListener("change", function () {
      const min = parseFloat(this.min) || 0;
      const max = parseFloat(this.max) || Number.MAX_SAFE_INTEGER;
      const value = parseFloat(this.value) || 0;

      if (value < min) {
        this.value = min;
      } else if (value > max) {
        this.value = max;
      }
    });
  });
});
