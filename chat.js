const USE_AI_FALLBACK = true;

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
  
  const systemMsg = {
    role: "user",
    parts: [{
      text: "You are an expert agricultural assistant named AgriBot. Provide detailed, accurate and helpful responses about farming, crops, weather impact, soil health, pest control, and sustainable agriculture practices. Format your answers with clear concise minimal paragraphs. If an image is provided, analyze it for crop diseases or pests. If asked about something outside agriculture except greetings, politely decline and refocus on farming topics."
    }]
  };
  let history = [systemMsg];

  // HTML escaping function to prevent XSS
  function escapeHtml(text) {
    return text
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#x27;');
  }

  // Secure message rendering function
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
    
    // Check if there is either text OR an image
    if (!input && !window.selectedImageBase64) return;

    if (input.length > 1000) {
      alert('Message too long. Please keep messages under 1000 characters.');
      return;
    }

    displayMessage(input || "Analyzing uploaded image...", 'user');
    chatInput.value = '';
    const typing = showTyping();
    toggleInput(true);

    try {
      let reply = "";
      
      // If there is an image or text, we go to backend (Gemini AI)
      if (USE_AI_FALLBACK && (window.selectedImageBase64 || input)) {
        
        // Prepare conceptual payload parts (not sent directly; the backend builds final payload)
        let userParts = [{ text: input || "Please identify this plant and check for diseases." }];
        
        // Add image data if exists (for documentation / future use)
        if (window.selectedImageBase64) {
          userParts.push({
            inline_data: {
              mime_type: "image/jpeg",
              data: window.selectedImageBase64
            }
          });
        }

        // Call backend /api/chat
        const res = await fetch(`${APP_CONFIG.API_BASE_URL}/api/chat`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify({
            message: input || "Identify crop and disease from image.",
            image: window.selectedImageBase64 || null   // backend expects 'image'
          })
        });

        if (res.ok) {
          const data = await res.json();
          // Backend already builds reply from Gemini response
          reply = data.reply || "I couldn't analyze that. Please try again.";
        } else {
          reply = "⚠️ API Error. Please check your API key.";
        }

      } else {
        // Fallback to JSON chatbot if AI is off
        reply = await jsonChatbot.getResponse(input);
      }
      
      setTimeout(() => {
        displayMessage(reply, 'bot');
        if (typeof clearImage === "function") clearImage(); // Clear preview after sending
      }, 600);
      
    } catch (error) {
      console.error('Chatbot Error:', error);
      displayMessage("⚠️ Connection error. Please try again!", 'bot');
    } finally {
      setTimeout(() => {
        typing.remove();
        toggleInput(false);
      }, 800);
    }
  });

  const addMessage = (who, txt) => {
    displayMessage(txt, who);
  };

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

  setTimeout(async () => {
    displayMessage('Hello! 🌱 I\'m AgriBot, your agricultural assistant. I can help you with farming questions or identify pests via photos. How can I assist you today?', 'bot');
  }, 500);

  chatInput.focus();
});