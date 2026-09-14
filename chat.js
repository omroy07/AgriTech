// AgriTech Assistant - Chat Interface & AI Vision Integration
const USE_AI_FALLBACK = true;
const CHAT_HISTORY_STORAGE_KEY = 'agritech_chat_history';

// Local storage prediction helper
function savePrediction(input, output) {
  try {
    const history = JSON.parse(localStorage.getItem("predictions")) || [];
    const newEntry = { input, output, timestamp: new Date().toLocaleString() };
    history.unshift(newEntry);
    localStorage.setItem("predictions", JSON.stringify(history.slice(0, 5)));
  } catch (err) {
    console.warn("Prediction saving failed:", err);
  }
}

// Rule-based fallback responses (offline mode)
const RULE_BASED_FALLBACKS = {
  soil: "Healthy soil is essential for good yields. Add organic compost, avoid excessive chemical use, and test soil regularly.",
  crop: "Crop management involves selecting suitable crops for the season, timely sowing, and monitoring pests and diseases.",
  crops: "Proper crop care includes crop rotation, pest control, balanced fertilization, and timely irrigation.",
  water: "Efficient water management includes drip or sprinkler irrigation and avoiding overwatering.",
  irrigation: "Irrigation should be scheduled based on crop growth stage and soil moisture levels.",
  fertilizer: "Fertilizers should be applied based on soil test results. Overuse can damage crops and soil health.",
  disease: "For crop diseases, early detection is critical. Remove infected leaves, apply recommended organic or chemical fungicides, and use our Disease Detector tool.",
  pest: "Manage pests using integrated pest management (IPM), neem oil sprays, pheromone traps, and bio-pesticides."
};

const DEFAULT_FALLBACK_MESSAGE =
  "I'm currently running in offline mode. Here's some general advice: focus on soil health, proper irrigation, balanced fertilization, and timely crop monitoring.";

const FALLBACK_MESSAGES = [
  "I did not fully catch that, but I can still help. Try asking about crop diseases, irrigation planning, or soil health.",
  "I could not find an exact answer yet. Ask me about crop recommendation, weather impact, pest control, or fertilizers.",
  "Let us try a more specific question. You can ask: best crops for your state, disease prevention, or water-saving techniques."
];

const MIN_TYPING_DELAY_MS = 600;
const MAX_TYPING_DELAY_MS = 2000;

document.addEventListener('DOMContentLoaded', () => {
  // Update copyright year dynamically
  const yearElement = document.getElementById('current-year');
  if (yearElement) {
    yearElement.textContent = new Date().getFullYear();
  }

  const chatContainer = document.getElementById('chat-container');
  const chatWindow = document.getElementById('chat-window');
  const chatForm = document.getElementById('chat-form');
  const chatInput = document.getElementById('chat-input');
  const sendBtn = document.getElementById('send-button');
  const clearChatBtn = document.getElementById('clear-chat-btn');

  // Photo upload elements
  const imageInput = document.getElementById('image-input');
  const uploadPhotoBtn = document.getElementById('upload-photo-btn');
  const imagePreviewContainer = document.getElementById('image-preview-container');
  const imagePreviewImg = document.getElementById('image-preview');
  const previewFilename = document.getElementById('preview-filename');
  const removeImageBtn = document.getElementById('remove-image-btn');
  const dropOverlay = document.getElementById('drop-overlay');

  // Lightbox modal elements
  const lightboxModal = document.getElementById('image-lightbox-modal');
  const lightboxImg = document.getElementById('lightbox-img');
  const lightboxCaption = document.getElementById('lightbox-caption');
  const lightboxCloseBtn = document.getElementById('lightbox-close-btn');
  const lightboxBackdrop = document.getElementById('lightbox-backdrop');

  // Active attached image state
  let currentImageDataUrl = null;
  let currentImageBase64 = null;
  let currentImageName = "";

  // Initialize JSON-based chatbot if available
  let jsonChatbot = null;
  if (typeof JSONChatbot === 'function') {
    jsonChatbot = new JSONChatbot();
  }

  let chatHistory = [];

  const persistChatHistory = () => {
    try {
      // Keep up to 30 recent messages in localStorage
      const historyToSave = chatHistory.slice(-30);
      localStorage.setItem(CHAT_HISTORY_STORAGE_KEY, JSON.stringify(historyToSave));
    } catch (error) {
      console.warn('Unable to persist chat history:', error);
    }
  };

  const loadChatHistory = () => {
    try {
      const rawHistory = localStorage.getItem(CHAT_HISTORY_STORAGE_KEY);
      const parsedHistory = rawHistory ? JSON.parse(rawHistory) : [];
      return Array.isArray(parsedHistory)
        ? parsedHistory.filter((entry) => entry && (typeof entry.messageContent === 'string' || entry.imageSrc) && (entry.sender === 'user' || entry.sender === 'bot'))
        : [];
    } catch (error) {
      console.warn('Unable to load chat history:', error);
      return [];
    }
  };

  const saveMessageToHistory = (messageContent, sender, time, imageSrc = null) => {
    chatHistory.push({
      messageContent,
      sender,
      time: time || new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      imageSrc: imageSrc || null
    });
    persistChatHistory();
  };

  const renderSavedHistory = () => {
    if (!chatHistory.length) return false;

    const welcomeMessage = chatWindow.querySelector('.welcome-message');
    if (welcomeMessage) {
      welcomeMessage.remove();
    }

    chatHistory.forEach(({ messageContent, sender, time, imageSrc }) => {
      displayMessage(messageContent, sender, time, false, imageSrc);
    });

    return true;
  };

  const clearChatHistory = () => {
    chatHistory = [];
    persistChatHistory();
    chatWindow.innerHTML = `
      <div class="welcome-message">
        <h3><i class="fas fa-leaf"></i> Welcome to AgriTech Assistant!</h3>
        <p>
          I'm powered by Google Gemini AI to help with all your farming
          questions and guide you through AgriTech platform features.
        </p>

        <div class="suggestions">
          <div class="suggestion">What can I do on AgriTech?</div>
          <div class="suggestion">How to use crop recommendation?</div>
          <div class="suggestion">Best crops for this season?</div>
          <div class="suggestion">Organic pest control methods</div>
          <div class="suggestion">Water conservation techniques</div>
          <div class="suggestion">Soil health improvement</div>
          <div class="suggestion">How to use crop disease detection?</div>
          <div class="suggestion">How does labour scheduling work?</div>
          <div class="suggestion">How to access farmer forum?</div>
          <div class="suggestion">How to check weather updates?</div>
          <div class="suggestion">Government schemes for farmers</div>
          <div class="suggestion">Fertilizer recommendations</div>
        </div>
      </div>
    `;
  };

  // HTML escaping function to prevent XSS
  function escapeHtml(text) {
    if (!text) return '';
    return String(text)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#x27;');
  }

  // Format message text (support markdown links, bold, italics, code)
  function format(txt) {
    if (!txt) return '';
    return txt
      .replace(/\n/g, '<br>')
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/`(.*?)`/g, '<code>$1</code>')
      .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener noreferrer" style="color:#22c55e;text-decoration:underline;">$1</a>');
  }

  // Lightbox controls
  const openLightbox = (imageSrc, captionText) => {
    if (!lightboxModal || !lightboxImg) return;
    lightboxImg.src = imageSrc;
    if (lightboxCaption) {
      lightboxCaption.textContent = captionText || "Crop diagnosis photo";
    }
    lightboxModal.style.display = 'flex';
    lightboxModal.setAttribute('aria-hidden', 'false');
  };

  const closeLightbox = () => {
    if (!lightboxModal) return;
    lightboxModal.style.display = 'none';
    lightboxModal.setAttribute('aria-hidden', 'true');
    if (lightboxImg) lightboxImg.src = '';
  };

  if (lightboxCloseBtn) lightboxCloseBtn.addEventListener('click', closeLightbox);
  if (lightboxBackdrop) lightboxBackdrop.addEventListener('click', closeLightbox);
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && lightboxModal && lightboxModal.style.display === 'flex') {
      closeLightbox();
    }
  });

  // Secure message rendering with optional image thumbnail
  function displayMessage(messageContent, sender, timeOverride, shouldPersist = true, imageSrc = null) {
    const welcomeMessage = chatWindow.querySelector('.welcome-message');
    if (welcomeMessage) {
      welcomeMessage.remove();
    }

    const messageElement = document.createElement('div');
    messageElement.className = `message ${sender}`;

    const time = timeOverride || new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    const name = sender === 'user' ? 'You' : 'AgriBot';

    const headerDiv = document.createElement('div');
    headerDiv.className = 'message-header';

    const icon = document.createElement('i');
    icon.className = `fas fa-${sender === 'user' ? 'user' : 'robot'}`;
    headerDiv.appendChild(icon);
    headerDiv.appendChild(document.createTextNode(` ${name}`));

    messageElement.appendChild(headerDiv);

    // If an image is associated with this message, render preview thumbnail
    if (imageSrc) {
      const imgContainer = document.createElement('div');
      imgContainer.className = 'message-image-container';

      const img = document.createElement('img');
      img.src = imageSrc;
      img.alt = 'Uploaded crop photo';
      img.className = 'message-image';
      img.addEventListener('click', () => openLightbox(imageSrc, messageContent || "Uploaded crop photo"));

      const zoomBadge = document.createElement('span');
      zoomBadge.className = 'image-zoom-badge';
      zoomBadge.innerHTML = '<i class="fas fa-search-plus"></i> View';

      imgContainer.appendChild(img);
      imgContainer.appendChild(zoomBadge);
      messageElement.appendChild(imgContainer);
    }

    if (messageContent) {
      const textDiv = document.createElement('div');
      textDiv.className = 'message-text';
      textDiv.innerHTML = format(escapeHtml(messageContent));
      messageElement.appendChild(textDiv);
    }

    const timeDiv = document.createElement('div');
    timeDiv.className = 'timestamp';
    timeDiv.textContent = time;
    messageElement.appendChild(timeDiv);

    chatWindow.appendChild(messageElement);
    chatWindow.scrollTop = chatWindow.scrollHeight;

    if (shouldPersist && !timeOverride) {
      saveMessageToHistory(messageContent, sender, time, imageSrc);
    }
  }

  // Handle image selection & preview
  const handleImageFile = (file) => {
    if (!file) return;

    if (!file.type.startsWith('image/')) {
      alert('Please select a valid image file (PNG, JPEG, WEBP).');
      return;
    }

    // Limit image size to 10MB
    if (file.size > 10 * 1024 * 1024) {
      alert('Image is too large. Please upload an image under 10MB.');
      return;
    }

    const reader = new FileReader();
    reader.onload = (e) => {
      currentImageDataUrl = e.target.result;
      currentImageBase64 = e.target.result.split(',')[1];
      currentImageName = file.name || "crop_photo.jpg";

      if (imagePreviewImg) {
        imagePreviewImg.src = currentImageDataUrl;
      }
      if (previewFilename) {
        const sizeKb = Math.round(file.size / 1024);
        previewFilename.innerHTML = `<i class="fas fa-image"></i> ${escapeHtml(currentImageName)} <small>(${sizeKb} KB)</small>`;
      }
      if (imagePreviewContainer) {
        imagePreviewContainer.style.display = 'flex';
      }
      chatInput.focus();
    };
    reader.readAsDataURL(file);
  };

  const clearImage = () => {
    currentImageDataUrl = null;
    currentImageBase64 = null;
    currentImageName = "";
    if (imageInput) imageInput.value = '';
    if (imagePreviewContainer) imagePreviewContainer.style.display = 'none';
    if (imagePreviewImg) imagePreviewImg.src = '';
  };

  // Attach event listeners for image upload button and input
  if (uploadPhotoBtn && imageInput) {
    uploadPhotoBtn.addEventListener('click', () => {
      imageInput.click();
    });
  }

  if (imageInput) {
    imageInput.addEventListener('change', (e) => {
      const file = e.target.files && e.target.files[0];
      if (file) handleImageFile(file);
    });
  }

  if (removeImageBtn) {
    removeImageBtn.addEventListener('click', clearImage);
  }

  // Drag and Drop Handling on Chat Container
  if (chatContainer) {
    let dragCounter = 0;

    chatContainer.addEventListener('dragenter', (e) => {
      e.preventDefault();
      e.stopPropagation();
      dragCounter++;
      chatContainer.classList.add('drag-active');
    });

    chatContainer.addEventListener('dragover', (e) => {
      e.preventDefault();
      e.stopPropagation();
    });

    chatContainer.addEventListener('dragleave', (e) => {
      e.preventDefault();
      e.stopPropagation();
      dragCounter--;
      if (dragCounter <= 0) {
        dragCounter = 0;
        chatContainer.classList.remove('drag-active');
      }
    });

    chatContainer.addEventListener('drop', (e) => {
      e.preventDefault();
      e.stopPropagation();
      dragCounter = 0;
      chatContainer.classList.remove('drag-active');

      const dt = e.dataTransfer;
      if (dt && dt.files && dt.files.length > 0) {
        const file = dt.files[0];
        if (file.type.startsWith('image/')) {
          handleImageFile(file);
        } else {
          alert('Please drop an image file (PNG, JPG, WEBP).');
        }
      }
    });
  }

  // Clipboard Paste Support (Ctrl+V)
  document.addEventListener('paste', (e) => {
    const items = (e.clipboardData || e.originalEvent.clipboardData)?.items;
    if (!items) return;

    for (let i = 0; i < items.length; i++) {
      if (items[i].type.indexOf('image') !== -1) {
        const file = items[i].getAsFile();
        if (file) {
          handleImageFile(file);
          break;
        }
      }
    }
  });

  // Suggestion pill clicks
  document.addEventListener('click', (e) => {
    if (e.target.classList.contains('suggestion')) {
      chatInput.value = e.target.textContent;
      chatForm.dispatchEvent(new Event('submit'));
    }
  });

  const delay = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

  const getRandomFallbackMessage = () => {
    const randomIndex = Math.floor(Math.random() * FALLBACK_MESSAGES.length);
    return FALLBACK_MESSAGES[randomIndex] || DEFAULT_FALLBACK_MESSAGE;
  };

  const getRuleBasedFallback = (input) => {
    const lowerInput = (input || '').toLowerCase();
    for (const keyword in RULE_BASED_FALLBACKS) {
      if (lowerInput.includes(keyword)) {
        return RULE_BASED_FALLBACKS[keyword];
      }
    }
    return getRandomFallbackMessage();
  };

  const resolveLocalResponse = async (input, hasImage = false) => {
    if (hasImage) {
      return "🌾 **Crop Image Received for Analysis**\n\nI have received your crop image! To get full live AI vision diagnostics with custom treatment steps, make sure our backend server is active with Gemini API configured.\n\n🔍 **Quick Diagnostic Guidelines**:\n- **Leaf Spot / Blight**: Remove diseased foliage and spray Copper Oxychloride or Mancozeb.\n- **Powdery Mildew / Rust**: Spray Neem oil (10,000 ppm) or wettable sulfur in early morning.\n- **Pest Infestation**: Look under leaves for aphids, thrips, or whiteflies.\n\n👉 **Recommended Tools**:\n- Try our specialized **[Crop Disease Detector](Disease prediction/template/index.html)**\n- Use our **[AI Disease Scanner](ai_disease.html)** for automated leaf pathology!";
    }

    if (jsonChatbot) {
      try {
        const details = await jsonChatbot.getResponseDetails(input);
        if (details && details.response) {
          return details.response;
        }
      } catch (error) {
        console.warn('Local response matching failed:', error);
      }
    }
    return getRuleBasedFallback(input);
  };

  const computeTypingDelay = (userInput, botReply, hasImage) => {
    const inputLength = (userInput || '').length;
    const replyLength = (botReply || '').length;
    const base = hasImage ? 900 : 600;
    const dynamic = Math.min(800, Math.floor((inputLength + replyLength) * 1.8));
    return Math.max(MIN_TYPING_DELAY_MS, Math.min(MAX_TYPING_DELAY_MS, base + dynamic));
  };

  const showTyping = (labelText) => {
    const typing = document.createElement('div');
    typing.className = 'typing-indicator';
    typing.innerHTML = `<div class="typing-text">${escapeHtml(labelText || 'AgriBot is typing')}</div><span></span><span></span><span></span>`;
    chatWindow.appendChild(typing);
    chatWindow.scrollTop = chatWindow.scrollHeight;
    return typing;
  };

  const setTypingText = (typingElement, text) => {
    if (!typingElement) return;
    const textElement = typingElement.querySelector('.typing-text');
    if (textElement) {
      textElement.textContent = text;
    }
  };

  const toggleInput = (disable) => {
    if (sendBtn) sendBtn.disabled = disable;
    if (chatInput) chatInput.disabled = disable;
    if (uploadPhotoBtn) uploadPhotoBtn.disabled = disable;
    if (!disable && chatInput) chatInput.focus();
  };

  // Chat Form Submission
  chatForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const input = chatInput.value.trim();
    const attachedImage = currentImageDataUrl;
    const attachedImageBase64 = currentImageBase64;

    // Must have either text or image
    if (!input && !attachedImageBase64) return;

    if (input.length > 1000) {
      alert('Message too long. Please keep messages under 1000 characters.');
      return;
    }

    // Render user message with attached image preview
    const userDisplayCaption = input || (attachedImage ? "Uploaded crop image for diagnosis" : "");
    displayMessage(userDisplayCaption, 'user', undefined, true, attachedImage);

    // Reset input fields and clear preview
    chatInput.value = '';
    chatInput.style.height = 'auto';
    clearImage();

    const hasImage = Boolean(attachedImageBase64);
    const typing = showTyping(hasImage ? 'AgriBot is analyzing your crop photo...' : 'AgriBot is typing...');
    toggleInput(true);
    const startedAt = Date.now();

    try {
      let reply = "";

      if (USE_AI_FALLBACK) {
        setTypingText(typing, hasImage ? 'Scanning plant pathology and symptoms...' : 'Consulting agricultural database...');

        try {
          const res = await fetch("/api/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              message: input || "Please identify this crop and diagnose any disease, pest, or deficiency shown in this image, and provide recommendations.",
              image: attachedImageBase64 || null
            })
          });

          if (res.ok) {
            const data = await res.json();
            reply = data.reply || "";
            if (reply) {
              savePrediction(input || "Crop photo diagnosis", reply);
            }
          }
        } catch (fetchErr) {
          console.info("Backend /api/chat not reachable, using offline assistant:", fetchErr.message);
        }
      }

      if (!reply) {
        reply = await resolveLocalResponse(input, hasImage);
      }

      setTypingText(typing, 'Finalizing response...');
      const typingDelay = computeTypingDelay(input, reply, hasImage);
      const elapsed = Date.now() - startedAt;
      if (elapsed < typingDelay) {
        await delay(typingDelay - elapsed);
      }

      displayMessage(reply || DEFAULT_FALLBACK_MESSAGE, 'bot');

    } catch (error) {
      console.error('Chatbot error:', error);
      const fallbackReply = await resolveLocalResponse(input, hasImage);
      displayMessage(fallbackReply, 'bot');
    } finally {
      if (typing) typing.remove();
      toggleInput(false);
    }
  });

  // Auto expand textarea on input
  chatInput.addEventListener('input', function () {
    this.style.height = 'auto';
    this.style.height = Math.min(this.scrollHeight, 150) + 'px';
  });

  // Enter to send, Shift+Enter for new line
  chatInput.addEventListener('keydown', function (e) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      chatForm.dispatchEvent(new Event('submit'));
    }
  });

  if (clearChatBtn) {
    clearChatBtn.addEventListener('click', clearChatHistory);
  }

  // Load chat history or show welcome message
  chatHistory = loadChatHistory();
  setTimeout(() => {
    if (!renderSavedHistory()) {
      displayMessage(
        "Hello! 🌱 I'm AgriBot, your AI farming assistant. You can ask me agriculture questions, seek crop recommendations, or **upload photos of your plants/crops** for disease diagnosis and treatment advice. How can I help you today?",
        'bot',
        undefined,
        false
      );
    }
  }, 400);

  chatInput.focus();
});