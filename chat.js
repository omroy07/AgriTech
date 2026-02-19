const USE_AI_FALLBACK = true;

// Rule-based fallback responses (offline mode)
const RULE_BASED_FALLBACKS = {
  soil: "Healthy soil is essential for good yields. Add organic compost, avoid excessive chemical use, and test soil regularly.",
  crop: "Crop management involves selecting suitable crops for the season, timely sowing, and monitoring pests and diseases.",
  crops: "Proper crop care includes crop rotation, pest control, balanced fertilization, and timely irrigation.",
  water: "Efficient water management includes drip or sprinkler irrigation and avoiding overwatering.",
  irrigation: "Irrigation should be scheduled based on crop growth stage and soil moisture levels.",
  fertilizer: "Fertilizers should be applied based on soil test results. Overuse can damage crops and soil health."
};

const DEFAULT_FALLBACK_MESSAGE =
  "I’m currently running in offline mode. Here’s some general advice: focus on soil health, proper irrigation, and timely crop care.";

document.addEventListener('DOMContentLoaded', () => {
  // --- BUG FIX: DYNAMIC COPYRIGHT YEAR ---
  const yearElement = document.getElementById('current-year');
  if (yearElement) {
    yearElement.textContent = new Date().getFullYear();
  }

  const chatWindow = document.getElementById('chat-window');
  const chatForm = document.getElementById('chat-form');
  const chatInput = document.getElementById('chat-input');
  const sendBtn = document.getElementById('send-button');

  // Initialize JSON-based chatbot
  const jsonChatbot = new JSONChatbot();

  // HTML escaping function to prevent XSS
  function escapeHtml(text) {
    return text
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#x27;');
  }

  // Secure message rendering
  function displayMessage(messageContent, sender) {
    const messageElement = document.createElement('div');
    messageElement.className = `message ${sender}`;

    const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    const name = sender === 'user' ? 'You' : 'AgriBot';

    const headerDiv = document.createElement('div');
    headerDiv.className = 'message-header';

    const icon = document.createElement('i');
    icon.className = `fas fa-${sender === 'user' ? 'user' : 'robot'}`;
    headerDiv.appendChild(icon);
    headerDiv.appendChild(document.createTextNode(` ${name}`));

    const textDiv = document.createElement('div');
    textDiv.className = 'message-text';
    textDiv.innerHTML = format(escapeHtml(messageContent));

    const timeDiv = document.createElement('div');
    timeDiv.className = 'timestamp';
    timeDiv.textContent = time;

    messageElement.appendChild(headerDiv);
    messageElement.appendChild(textDiv);
    messageElement.appendChild(timeDiv);

    chatWindow.appendChild(messageElement);
    chatWindow.scrollTop = chatWindow.scrollHeight;
  }

  document.addEventListener('click', (e) => {
    if (e.target.classList.contains('suggestion')) {
      chatInput.value = e.target.textContent;
      chatForm.dispatchEvent(new Event('submit'));
    }
  });

  chatForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const input = chatInput.value.trim();

    if (!input && !window.selectedImageBase64) return;

    if (input.length > 1000) {
      alert('Message too long. Please keep messages under 1000 characters.');
      return;
    }

    displayMessage(input || "Analyzing uploaded image...", 'user');
    chatInput.value = '';
    chatInput.style.height = 'auto';

    const typing = showTyping();
    toggleInput(true);

    try {
      let reply = "";

      if (USE_AI_FALLBACK && (window.selectedImageBase64 || input)) {
        const res = await fetch("/api/chat", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            message: input || "Identify crop and disease from image.",
            image: window.selectedImageBase64 || null
          })
        });

        if (res.ok) {
          const data = await res.json();
          reply = data.reply || DEFAULT_FALLBACK_MESSAGE;
        } else {
          // Rule-based fallback on API failure
          const lowerInput = input.toLowerCase();
          reply = DEFAULT_FALLBACK_MESSAGE;

          for (const keyword in RULE_BASED_FALLBACKS) {
            if (lowerInput.includes(keyword)) {
              reply = RULE_BASED_FALLBACKS[keyword];
              break;
            }
          }
        }
      } else {
        reply = await jsonChatbot.getResponse(input);
      }

      setTimeout(() => {
        displayMessage(reply, 'bot');
        if (typeof clearImage === "function") clearImage();
      }, 600);

    } catch (error) {
      console.error('Chatbot Error:', error);

      const lowerInput = input.toLowerCase();
      let fallbackReply = DEFAULT_FALLBACK_MESSAGE;

      for (const keyword in RULE_BASED_FALLBACKS) {
        if (lowerInput.includes(keyword)) {
          fallbackReply = RULE_BASED_FALLBACKS[keyword];
          break;
        }
      }

      displayMessage(fallbackReply, 'bot');
    } finally {
      setTimeout(() => {
        typing.remove();
        toggleInput(false);
      }, 800);
    }
  });

  const showTyping = () => {
    const typing = document.createElement('div');
    typing.className = 'typing-indicator';
    typing.innerHTML = `<div>AgriBot is typing</div><span></span><span></span><span></span>`;
    chatWindow.appendChild(typing);
    chatWindow.scrollTop = chatWindow.scrollHeight;
    return typing;
  };

  const toggleInput = (disable) => {
    sendBtn.disabled = disable;
    chatInput.disabled = disable;
    if (!disable) chatInput.focus();
  };

  const format = (txt) =>
    txt.replace(/\n/g, '<br>')
       .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
       .replace(/\*(.*?)\*/g, '<em>$1</em>')
       .replace(/`(.*?)`/g, '<code>$1</code>');

  setTimeout(() => {
    displayMessage(
      "Hello! 🌱 I'm AgriBot, your AI assistant for AgriTech platform and farming guidance. I can help you navigate our tools, answer agriculture questions, recommend crops based on your region and season, and provide farming advice. How can I assist you today?",
      'bot'
    );
  }, 500);

  chatInput.focus();
});

// 🌙 GLOBAL DARK/LIGHT MODE FIX (Mobile + Desktop Toggle)
document.addEventListener("DOMContentLoaded", function () {
  const toggleButtons = document.querySelectorAll(".theme-toggle, .nav-btn");

  toggleButtons.forEach((btn) => {
    // Only attach to buttons that contain Dark or Light text
    if (
      btn.textContent.toLowerCase().includes("dark") ||
      btn.textContent.toLowerCase().includes("light")
    ) {
      btn.addEventListener("click", function (e) {
        e.stopPropagation(); // critical for mobile sidebar overlay

        document.body.classList.toggle("dark-mode");

        // Save theme preference
        if (document.body.classList.contains("dark-mode")) {
          localStorage.setItem("theme", "dark");
          btn.innerHTML = "☀️ Light Mode";
        } else {
          localStorage.setItem("theme", "light");
          btn.innerHTML = "🌙 Dark Mode";
        }
      });
    }
  });

  // Apply saved theme on page load
  const savedTheme = localStorage.getItem("theme");
  if (savedTheme === "dark") {
    document.body.classList.add("dark-mode");
  }
});

const chatInput = document.getElementById("chat-input");
const chatForm = document.getElementById("chat-form");

// Auto expand textarea
chatInput.addEventListener("input", function () {
  this.style.height = "auto";
  this.style.height = this.scrollHeight + "px";
});

// Enter vs Shift+Enter
chatInput.addEventListener("keydown", function (e) {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    chatForm.dispatchEvent(new Event("submit"));
  }
});