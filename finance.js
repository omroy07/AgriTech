document.addEventListener('DOMContentLoaded', () => {
  const chatWindow = document.getElementById('chat-window');
  const chatForm = document.getElementById('chat-form');
  const chatInput = document.getElementById('chat-input');
  const sendBtn = document.getElementById('send-button');
  const farmerForm = document.getElementById('farmer-form');

  // Gemini AI configuration
  const API_KEY = 'GEMINI_API_KEY'; // get api key from https://ai.google.dev/
  const API_URL = `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key=${API_KEY}`;

  const systemMsg = {
    role: "user",
    parts: [{ text: "You are a financial advisor specializing in agricultural loans and financial support for farmers in India. Provide detailed, accurate advice on loans, insurance, subsidies, investment opportunities, and financial planning for farming. Focus on Indian banking schemes, NABARD, cooperative banks, and government programs. Format answers clearly and helpfully. Politely decline non-agricultural finance topics." }]
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
    if (!chatWindow) return; // If no chat window, skip
    const messageElement = document.createElement('div');
    messageElement.className = `message ${sender}`;
    const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    const name = sender === 'user' ? 'You' : 'FinanceBot';

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
    timeDiv.className = 'message-time';
    timeDiv.textContent = time;

    messageElement.appendChild(headerDiv);
    messageElement.appendChild(textDiv);
    messageElement.appendChild(timeDiv);

    chatWindow.appendChild(messageElement);
    chatWindow.scrollTop = chatWindow.scrollHeight;

    // Animate message appearance
    setTimeout(() => {
      messageElement.style.opacity = '1';
      messageElement.style.transform = 'translateY(0)';
    }, 10);
  }

  // Show typing indicator
  function showTyping() {
    if (!chatWindow) return null;
    const typingElement = document.createElement('div');
    typingElement.className = 'message bot typing';
    typingElement.innerHTML = `
      <div class="message-header">
        <i class="fas fa-robot"></i> FinanceBot
      </div>
      <div class="message-text">
        <div class="typing-indicator">
          <span></span><span></span><span></span>
        </div>
      </div>
    `;
    chatWindow.appendChild(typingElement);
    chatWindow.scrollTop = chatWindow.scrollHeight;
    return typingElement;
  }

  // Format message text (basic markdown-like formatting)
  function format(text) {
    return text
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/\n/g, '<br>');
  }

  // Local recommendation function using prompt engineering logic
  function recommendScheme(data) {
    let recommendation = "Based on your profile, here are the recommended government schemes:\n\n";

    // Farmer type based logic
    if (data['farmer-type'] === 'small') {
      recommendation += "• **PM-KISAN**: Direct income support of ₹6,000 per year for small farmers.\n";
    } else if (data['farmer-type'] === 'marginal') {
      recommendation += "• **PM-KISAN**: Income support for marginal farmers.\n";
      recommendation += "• **Pradhan Mantri Fasal Bima Yojana**: Crop insurance for risk mitigation.\n";
    }

    // Land size based
    const landSize = parseFloat(data['land-size']) || 0;
    if (landSize < 2) {
      recommendation += "• **Marginal Farmer Schemes**: Focus on small landholding support.\n";
    } else if (landSize >= 2 && landSize <= 5) {
      recommendation += "• **Small Farmer Credit**: Easy loan access through KCC.\n";
    }

    // Crops based
    const crops = data['crops']?.toLowerCase() || '';
    if (crops.includes('rice') || crops.includes('wheat')) {
      recommendation += "• **MSP Schemes**: Minimum Support Price for rice/wheat.\n";
    }
    if (data['farming-method'] === 'organic') {
      recommendation += "• **Paramparagat Krishi Vikas Yojana**: Organic farming support.\n";
    }

    // Income based
    const income = parseFloat(data['income']) || 0;
    if (income < 100000) {
      recommendation += "• **Subsidies under Agriculture Infrastructure Fund**: For low-income farmers.\n";
    }

    // Irrigation
    if (data['irrigation'] === 'rainfed') {
      recommendation += "• **Per Drop More Crop**: Micro-irrigation subsidies.\n";
    }

    // KYC and banking
    if (data['kyc'] === 'completed' && data['aadhaar-linked'] === 'yes') {
      recommendation += "• **DBT Schemes**: Direct Benefit Transfers available.\n";
    }

    // State specific (basic)
    const state = data['state']?.toLowerCase() || '';
    if (state.includes('maharashtra')) {
      recommendation += "• **Mahatma Gandhi National Rural Employment Guarantee Act**: Additional employment support.\n";
    }

    if (recommendation === "Based on your profile, here are the recommended government schemes:\n\n") {
      recommendation += "• **General Agricultural Schemes**: PM-KISAN, Soil Health Card, Kisan Credit Card.\n";
    }

    recommendation += "\n**Note**: Please verify eligibility and apply through official channels. Consult local agriculture office for personalized advice.";

    return recommendation;
  }

  // Handle farmer form submission
  if (farmerForm) {
    farmerForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      console.log('Form submitted');

      // Collect form data
      const formData = new FormData(farmerForm);
      const data = {};
      for (let [key, value] of formData.entries()) {
        data[key] = value;
      }
      console.log('Form data:', data);

      // Display user submission
      displayMessage(`Submitted farmer details: ${JSON.stringify(data, null, 2)}`, 'user');

      // Generate recommendation locally
      const reply = recommendScheme(data);

      displayMessage(reply, 'bot');

      // If no chat window, display result on page
      if (!chatWindow) {
        let resultDiv = document.getElementById('result-output');
        if (!resultDiv) {
          resultDiv = document.createElement('div');
          resultDiv.id = 'result-output';
          resultDiv.style.cssText = `
            margin-top: 2rem;
            padding: 1rem;
            background: #f0f9ff;
            border: 1px solid #3b82f6;
            border-radius: 8px;
            max-width: 700px;
            margin-left: auto;
            margin-right: auto;
          `;
          farmerForm.insertAdjacentElement('afterend', resultDiv);
        }
        resultDiv.innerHTML = `<h3>Recommended Government Scheme</h3><p>${format(reply)}</p>`;
      }
    });
  }

  // Handle chat form submission (if chat interface exists)
  if (chatForm) {
    chatForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const input = chatInput.value.trim();
      if (!input) return;

      displayMessage(input, 'user');
      chatInput.value = '';

      const typing = showTyping();

      try {
        const res = await fetch(API_URL, {
          method: 'POST',
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            contents: [
              { role: "user", parts: [{ text: systemMsg.parts[0].text }] },
              { role: "user", parts: [{ text: input }] }
            ],
            generationConfig: {
              temperature: 0.7,
              maxOutputTokens: 500,
              topP: 0.8,
              topK: 40
            }
          })
        });

        let reply = "⚠️ Sorry, I couldn't process that.";
        if (res.ok) {
          const data = await res.json();
          reply = data?.candidates?.[0]?.content?.parts?.[0]?.text || reply;
        }

        typing.remove();
        displayMessage(reply, 'bot');

      } catch (error) {
        console.error("Gemini error:", error);
        typing.remove();
        displayMessage("⚠️ I'm having trouble right now. Please try again later!", 'bot');
      }
    });

    // Send button click
    if (sendBtn) {
      sendBtn.addEventListener('click', () => {
        chatForm.dispatchEvent(new Event('submit'));
      });
    }

    // Enter key to send
    chatInput.addEventListener('keypress', (e) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        chatForm.dispatchEvent(new Event('submit'));
      }
    });

    // Initial welcome message
    setTimeout(() => {
      displayMessage("Hello! I'm FinanceBot, your agricultural finance advisor. How can I help you with loans, insurance, or financial planning for farming?", 'bot');
    }, 500);
  }
});