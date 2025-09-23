document.addEventListener('DOMContentLoaded', () => {
  const chatWindow = document.getElementById('chat-window');
  const chatForm = document.getElementById('chat-form');
  const chatInput = document.getElementById('chat-input');
  const sendBtn = document.getElementById('send-button');

  // Initialize JSON-based chatbot
  const jsonChatbot = new JSONChatbot();
  
  // Gemini AI fallback configuration
  const API_KEY = 'GEMINI_API_KEY'; // get api key from https://ai.google.dev/
  const API_URL = `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key=${API_KEY}`;
  const USE_AI_FALLBACK = false; // Set to true if you want to use Gemini AI as fallback
  
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

    try {
      // Try JSON chatbot first
      let reply = await jsonChatbot.getResponse(input);
      
      // If JSON chatbot returns a fallback and AI is enabled, try Gemini AI
      if (USE_AI_FALLBACK && reply.includes("Sorry, I didn't understand")) {
        console.log('Falling back to Gemini AI...');
        history.push({ role: "user", parts: [{ text: input }] });
        
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

        if (res.ok) {
          const data = await res.json();
          const aiReply = data?.candidates?.[0]?.content?.parts?.[0]?.text;
          if (aiReply) {
            reply = aiReply;
            history.push({ role: "model", parts: [{ text: reply }] });
          }
        }
      }
      
      // Add smooth animation delay for more natural feel
      setTimeout(() => {
        displayMessage(reply, 'bot');
      }, Math.random() * 800 + 400); // Random delay between 400-1200ms
      
    } catch (error) {
      console.error('Chatbot Error:', error);
      setTimeout(() => {
        displayMessage("⚠️ I'm having trouble right now. Please try asking your question again!", 'bot');
      }, 500);
    } finally {
      setTimeout(() => {
        typing.remove();
        toggleInput(false);
      }, Math.random() * 800 + 600); // Remove typing indicator after response
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

  // Initialize chatbot with welcome message
  setTimeout(async () => {
    await jsonChatbot.getResponse('hello').then(welcomeMsg => {
      displayMessage(welcomeMsg, 'bot');
    }).catch(() => {
      displayMessage('Hello! 🌱 I\'m AgriBot, your agricultural assistant. I can help you with farming questions, crop management, soil health, pest control, and more. How can I assist you today?', 'bot');
    });
  }, 500);

  chatInput.focus();
});