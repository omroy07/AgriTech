import { initializeApp } from "https://www.gstatic.com/firebasejs/10.11.0/firebase-app.js";
import { getAuth, GoogleAuthProvider, signInWithPopup, sendPasswordResetEmail } from "https://www.gstatic.com/firebasejs/10.11.0/firebase-auth.js";

// Secure Firebase configuration - fetched from server
let firebaseConfig = null;
let app = null;
let auth = null;

// Initialize Firebase securely
async function initializeFirebase() {
  try {
    const response = await fetch(`${APP_CONFIG.API_BASE_URL}/api/firebase-config`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    firebaseConfig = await response.json();
    
    // Validate that we have the required configuration
    if (!firebaseConfig.apiKey || !firebaseConfig.authDomain || !firebaseConfig.projectId) {
      throw new Error('Incomplete Firebase configuration received from server');
    }
    
    app = initializeApp(firebaseConfig);
    auth = getAuth(app);
    auth.languageCode = 'en';
    
    console.log('Firebase initialized successfully');
    return true;
  } catch (error) {
    console.error('Failed to initialize Firebase:', error);
    return false;
  }
}

const provider = new GoogleAuthProvider();

// Handle Google Login and Password Reset
async function setupFirebaseAuth() {
  const initialized = await initializeFirebase();
  if (!initialized) {
    console.error('Firebase initialization failed. Google login will not work.');
    return;
  }
  
  const googleLogin = document.getElementById("google-login-btn");
  if (googleLogin) {
    googleLogin.addEventListener("click", async function () {
      try {
        const result = await signInWithPopup(auth, provider);
        const credential = GoogleAuthProvider.credentialFromResult(result);
        const user = result.user;
        console.log(user);
        window.location.href = "index.html"; // Redirect to home page after successful login
      } catch (error) {  
        const errorCode = error.code;
        const errorMessage = error.message;

        console.error("Google sign-in error:", errorCode, errorMessage);

        // Show user-friendly message
        switch (errorCode) {
          case 'auth/popup-closed-by-user':
            alert("Sign-in popup was closed before completing. Please try again.");
            break;
          case 'auth/cancelled-popup-request':
            alert("Multiple sign-in attempts detected. Please wait and try again.");
            break;
          case 'auth/popup-blocked':
            alert("Popup was blocked by the browser. Please allow popups and try again.");
            break;
          case 'auth/network-request-failed':
            alert("Network error occurred. Check your connection and try again.");
            break;
          default:
            alert("Google sign-in failed. Please try again later.");
        }
      }
    });
  }

  // Handle forgot password form submission
  const forgotPasswordForm = document.getElementById("forgot-password-form");
  if (forgotPasswordForm) {
    forgotPasswordForm.addEventListener("submit", async (event) => {
      event.preventDefault();
      const emailInput = document.getElementById('email');
      const resetBtn = document.getElementById('reset-btn');
      const resetText = document.getElementById('reset-text');

      const email = emailInput.value.trim();
      if (!email) {
        alert("Please enter a valid email address.");
        return;
      }

      // Add loading state
      resetBtn.classList.add('loading');
      resetText.textContent = 'Sending...';
      resetBtn.disabled = true;

      try {
        await sendPasswordResetEmail(auth, email);
        alert("A password reset link has been sent to your email. Please check your inbox.");
        // Redirect to login page after a short delay
        setTimeout(() => {
          window.location.href = 'login.html';
        }, 3000);
      } catch (error) {
        const errorCode = error.code;
        const errorMessage = error.message;
        console.error("Password reset error:", errorCode, errorMessage);
        
        // Show user-friendly error message
        switch (errorCode) {
          case 'auth/invalid-email':
            alert("The email address is not valid.");
            break;
          case 'auth/user-not-found':
            alert("No account found with this email address.");
            break;
          default:
            alert("Failed to send password reset email. Please try again.");
            break;
        }

        resetBtn.classList.remove('loading');
        resetText.textContent = 'Reset Password';
        resetBtn.disabled = false;
      }
    });
  }
}

// Initialize Firebase authentication when the script loads
setupFirebaseAuth();