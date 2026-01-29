/**
 * Voice Input Module for AgriTech
 * Provides voice-to-text functionality for all forms
 * Supports multiple languages for accessibility
 */

class VoiceInputManager {
  constructor() {
    this.recognition = null;
    this.isListening = false;
    this.currentInput = null;
    this.supportedLanguages = {
      'en-IN': 'English (India)',
      'hi-IN': 'Hindi (हिंदी)',
      'ta-IN': 'Tamil (தமிழ்)',
      'te-IN': 'Telugu (తెలుగు)',
      'mr-IN': 'Marathi (मराठी)',
      'bn-IN': 'Bengali (বাংলা)',
      'gu-IN': 'Gujarati (ગુજરાતી)',
      'kn-IN': 'Kannada (ಕನ್ನಡ)',
      'pa-IN': 'Punjabi (ਪੰਜਾਬੀ)',
      'ml-IN': 'Malayalam (മലയാളം)'
    };
    this.currentLanguage = 'en-IN';
    this.initializeRecognition();
  }

  initializeRecognition() {
    // Check if browser supports Web Speech API
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
      console.warn('Web Speech API not supported in this browser');
      return false;
    }

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    this.recognition = new SpeechRecognition();
    
    // Configure recognition
    this.recognition.continuous = false;
    this.recognition.interimResults = false;
    this.recognition.maxAlternatives = 1;
    this.recognition.lang = this.currentLanguage;

    // Set up event handlers
    this.recognition.onstart = () => {
      this.isListening = true;
      this.updateButtonState(this.currentInput, 'listening');
      this.showFeedback('Listening... Speak now', 'info');
    };

    this.recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      const confidence = event.results[0][0].confidence;
      
      if (this.currentInput) {
        // Append to existing text or replace
        const currentValue = this.currentInput.value.trim();
        if (currentValue) {
          this.currentInput.value = currentValue + ' ' + transcript;
        } else {
          this.currentInput.value = transcript;
        }
        
        // Trigger input event for any listeners
        this.currentInput.dispatchEvent(new Event('input', { bubbles: true }));
      }
      
      this.showFeedback(`Captured: "${transcript}" (${Math.round(confidence * 100)}% confidence)`, 'success');
    };

    this.recognition.onerror = (event) => {
      this.isListening = false;
      this.updateButtonState(this.currentInput, 'error');
      
      let errorMessage = 'Voice input error: ';
      switch(event.error) {
        case 'no-speech':
          errorMessage += 'No speech detected. Please try again.';
          break;
        case 'audio-capture':
          errorMessage += 'Microphone not accessible. Check permissions.';
          break;
        case 'not-allowed':
          errorMessage += 'Microphone permission denied.';
          break;
        case 'network':
          errorMessage += 'Network error. Check your connection.';
          break;
        default:
          errorMessage += event.error;
      }
      
      this.showFeedback(errorMessage, 'error');
    };

    this.recognition.onend = () => {
      this.isListening = false;
      this.updateButtonState(this.currentInput, 'ready');
    };

    return true;
  }

  setLanguage(langCode) {
    if (this.supportedLanguages[langCode]) {
      this.currentLanguage = langCode;
      if (this.recognition) {
        this.recognition.lang = langCode;
      }
      localStorage.setItem('agritech_voice_lang', langCode);
    }
  }

  startListening(inputElement) {
    if (!this.recognition) {
      this.showFeedback('Voice input not supported in your browser', 'error');
      return;
    }

    if (this.isListening) {
      this.stopListening();
      return;
    }

    this.currentInput = inputElement;
    
    try {
      this.recognition.start();
    } catch (error) {
      console.error('Recognition start error:', error);
      this.showFeedback('Failed to start voice input. Please try again.', 'error');
    }
  }

  stopListening() {
    if (this.recognition && this.isListening) {
      this.recognition.stop();
    }
  }

  updateButtonState(inputElement, state) {
    if (!inputElement) return;
    
    const button = inputElement.parentElement?.querySelector('.voice-btn');
    if (!button) return;

    button.classList.remove('listening', 'error', 'ready');
    button.classList.add(state);

    const icon = button.querySelector('i');
    if (icon) {
      switch(state) {
        case 'listening':
          icon.className = 'fas fa-microphone-slash';
          button.title = 'Stop listening';
          break;
        case 'error':
          icon.className = 'fas fa-exclamation-circle';
          button.title = 'Error - click to retry';
          setTimeout(() => {
            icon.className = 'fas fa-microphone';
            button.title = 'Click to speak';
            button.classList.remove('error');
          }, 3000);
          break;
        default:
          icon.className = 'fas fa-microphone';
          button.title = 'Click to speak';
      }
    }
  }

  showFeedback(message, type = 'info') {
    // Create or update feedback element
    let feedback = document.getElementById('voice-feedback');
    
    if (!feedback) {
      feedback = document.createElement('div');
      feedback.id = 'voice-feedback';
      feedback.style.cssText = `
        position: fixed;
        top: 80px;
        right: 20px;
        max-width: 300px;
        padding: 12px 16px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        z-index: 10000;
        font-size: 14px;
        animation: slideIn 0.3s ease-out;
        display: flex;
        align-items: center;
        gap: 8px;
      `;
      document.body.appendChild(feedback);
    }

    // Set colors based on type
    const colors = {
      info: { bg: '#e3f2fd', border: '#2196f3', text: '#0d47a1' },
      success: { bg: '#e8f5e9', border: '#4caf50', text: '#1b5e20' },
      error: { bg: '#ffebee', border: '#f44336', text: '#c62828' }
    };

    const color = colors[type] || colors.info;
    feedback.style.backgroundColor = color.bg;
    feedback.style.borderLeft = `4px solid ${color.border}`;
    feedback.style.color = color.text;

    const icon = type === 'success' ? '✓' : type === 'error' ? '✕' : 'ℹ';
    feedback.innerHTML = `<strong>${icon}</strong> ${message}`;

    // Auto-hide after 4 seconds
    setTimeout(() => {
      feedback.style.animation = 'slideOut 0.3s ease-out';
      setTimeout(() => feedback.remove(), 300);
    }, 4000);
  }

  // Add voice button to input field
  addVoiceButton(inputElement, options = {}) {
    if (!this.recognition) {
      return; // Don't add button if not supported
    }

    // Check if button already exists
    if (inputElement.parentElement?.querySelector('.voice-btn')) {
      return;
    }

    const wrapper = document.createElement('div');
    wrapper.className = 'voice-input-wrapper';
    wrapper.style.position = 'relative';
    wrapper.style.display = 'inline-block';
    wrapper.style.width = '100%';

    // Wrap the input
    inputElement.parentNode.insertBefore(wrapper, inputElement);
    wrapper.appendChild(inputElement);

    // Create voice button
    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'voice-btn ready';
    button.title = 'Click to speak';
    button.innerHTML = '<i class="fas fa-microphone"></i>';
    button.style.cssText = `
      position: absolute;
      right: 8px;
      top: 50%;
      transform: translateY(-50%);
      background: linear-gradient(135deg, #4caf50, #66bb6a);
      border: none;
      border-radius: 50%;
      width: 36px;
      height: 36px;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      color: white;
      font-size: 16px;
      box-shadow: 0 2px 8px rgba(76,175,80,0.3);
      transition: all 0.3s ease;
      z-index: 10;
    `;

    button.addEventListener('click', (e) => {
      e.preventDefault();
      this.startListening(inputElement);
    });

    // Hover effect
    button.addEventListener('mouseenter', () => {
      button.style.transform = 'translateY(-50%) scale(1.1)';
      button.style.boxShadow = '0 4px 12px rgba(76,175,80,0.4)';
    });

    button.addEventListener('mouseleave', () => {
      if (!this.isListening) {
        button.style.transform = 'translateY(-50%) scale(1)';
        button.style.boxShadow = '0 2px 8px rgba(76,175,80,0.3)';
      }
    });

    wrapper.appendChild(button);

    // Adjust input padding to prevent text overlap
    const currentPaddingRight = window.getComputedStyle(inputElement).paddingRight;
    inputElement.style.paddingRight = `${parseInt(currentPaddingRight) + 45}px`;
  }

  // Initialize all voice inputs on a page
  initializePageVoiceInputs(selector = 'input[type="text"], input[type="search"], textarea') {
    const inputs = document.querySelectorAll(selector);
    inputs.forEach(input => {
      // Skip if already initialized or has data-no-voice attribute
      if (input.hasAttribute('data-no-voice') || input.parentElement?.classList.contains('voice-input-wrapper')) {
        return;
      }
      
      // Only add to visible inputs
      if (input.offsetParent !== null) {
        this.addVoiceButton(input);
      }
    });
  }

  // Create language selector
  createLanguageSelector(containerElement) {
    const selector = document.createElement('div');
    selector.className = 'voice-language-selector';
    selector.style.cssText = `
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 6px 12px;
      background: rgba(76, 175, 80, 0.1);
      border-radius: 20px;
      font-size: 13px;
    `;

    const label = document.createElement('span');
    label.innerHTML = '<i class="fas fa-language"></i> Voice:';
    label.style.color = '#4caf50';
    label.style.fontWeight = '600';

    const select = document.createElement('select');
    select.style.cssText = `
      border: none;
      background: transparent;
      color: #333;
      font-size: 13px;
      cursor: pointer;
      outline: none;
    `;

    Object.entries(this.supportedLanguages).forEach(([code, name]) => {
      const option = document.createElement('option');
      option.value = code;
      option.textContent = name;
      select.appendChild(option);
    });

    // Load saved language preference
    const savedLang = localStorage.getItem('agritech_voice_lang') || 'en-IN';
    select.value = savedLang;
    this.setLanguage(savedLang);

    select.addEventListener('change', (e) => {
      this.setLanguage(e.target.value);
      this.showFeedback(`Voice language changed to ${this.supportedLanguages[e.target.value]}`, 'success');
    });

    selector.appendChild(label);
    selector.appendChild(select);
    containerElement.appendChild(selector);
  }
}

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
  @keyframes slideIn {
    from {
      transform: translateX(400px);
      opacity: 0;
    }
    to {
      transform: translateX(0);
      opacity: 1;
    }
  }

  @keyframes slideOut {
    from {
      transform: translateX(0);
      opacity: 1;
    }
    to {
      transform: translateX(400px);
      opacity: 0;
    }
  }

  .voice-btn.listening {
    background: linear-gradient(135deg, #f44336, #e57373) !important;
    animation: pulse 1.5s ease-in-out infinite;
  }

  .voice-btn.error {
    background: linear-gradient(135deg, #ff9800, #ffb74d) !important;
  }

  @keyframes pulse {
    0%, 100% {
      transform: translateY(-50%) scale(1);
      box-shadow: 0 2px 8px rgba(244,67,54,0.3);
    }
    50% {
      transform: translateY(-50%) scale(1.1);
      box-shadow: 0 4px 16px rgba(244,67,54,0.5);
    }
  }

  /* Dark mode support */
  [data-theme="dark"] .voice-btn {
    box-shadow: 0 2px 8px rgba(76,175,80,0.5);
  }

  [data-theme="dark"] #voice-feedback {
    box-shadow: 0 4px 12px rgba(0,0,0,0.4);
  }
`;
document.head.appendChild(style);

// Create global instance
const voiceInputManager = new VoiceInputManager();

// Auto-initialize when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    voiceInputManager.initializePageVoiceInputs();
  });
} else {
  voiceInputManager.initializePageVoiceInputs();
}
