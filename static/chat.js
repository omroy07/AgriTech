document.addEventListener('DOMContentLoaded', () => {
  const chatWindow = document.getElementById('chat-window');
  const chatForm = document.getElementById('chat-form');
  const chatInput = document.getElementById('chat-input');
  const sendBtn = document.getElementById('send-button');

  const API_KEY = 'GEMINI_API_KEY'; // get api key from https://ai.google.dev/
  const API_URL = `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key=${API_KEY}`;
  
  const systemMsg = {
    role: "user",
    parts: [{ text: "You are an expert agricultural assistant named AgriBot. Provide detailed, accurate and helpful responses about farming, crops, weather impact, soil health, pest control, and sustainable agriculture practices. Format your answers with clear concise minimal paragraphs. If asked about something outside agriculture except greetings, politely decline and refocus on farming topics." }]
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
    
    // Create message header
    const headerDiv = document.createElement('div');
    headerDiv.className = 'message-header';
    const icon = document.createElement('i');
    icon.className = `fas fa-${sender === 'user' ? 'user' : 'robot'}`;
    headerDiv.appendChild(icon);
    headerDiv.appendChild(document.createTextNode(` ${name}`));
    
    // Create message text (safely formatted)
    const textDiv = document.createElement('div');
    textDiv.className = 'message-text';
    textDiv.innerHTML = format(escapeHtml(messageContent)); // Safe formatting after escaping
    
    // Create timestamp
    const timeDiv = document.createElement('div');
    timeDiv.className = 'timestamp';
    timeDiv.textContent = time;
    
    // Assemble message
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
    if (!input) return;

    // Input validation - limit message length
    if (input.length > 1000) {
      alert('Message too long. Please keep messages under 1000 characters.');
      return;
    }

    displayMessage(input, 'user');
    chatInput.value = '';
    const typing = showTyping();
    toggleInput(true);
    history.push({ role: "user", parts: [{ text: input }] });

    try {
      const res = await fetch(API_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          contents: history,
          generationConfig: { 
            temperature: 0.7, 
            maxOutputTokens: 1000,
            topP: 0.8,
            topK: 40
          }
        })
      });

      if (!res.ok) {
        throw new Error(`HTTP error! status: ${res.status}`);
      }

      const data = await res.json();
      console.log('API Response:', data);
      
      const reply = data?.candidates?.[0]?.content?.parts?.[0]?.text || "⚠️ I didn't receive a proper response. Please try again.";
      displayMessage(reply, 'bot');
      history.push({ role: "model", parts: [{ text: reply }] });
    } catch (error) {
      console.error('Error:', error);
      displayMessage("⚠️ I'm having trouble connecting right now. Please check your internet connection and try again.", 'bot');
    } finally {
      typing.remove();
      toggleInput(false);
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

  setTimeout(() => {
    displayMessage('Hello! 🌱 I\'m AgriBot, your agricultural assistant. I can help you with farming questions, crop management, soil health, pest control, and more. How can I assist you today?', 'bot');
  }, 500);

  chatInput.focus();
});