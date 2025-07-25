const chatWindow = document.getElementById('chat-window');
    const chatForm = document.getElementById('chat-form');
    const chatInput = document.getElementById('chat-input');

    const responses = {
      'hello': 'Hello! How can I assist you with your farming needs today?',
      'hi': 'Hi there! Need any agricultural advice?',
      'weather': 'The weather today is sunny with a chance of rain in the evening.',
      'crop': 'For this season, rice and maize are good choices.',
      'fertilizer': 'Using organic compost is beneficial for soil health.',
      'market': 'The current market price for wheat is ₹2,000 per quintal.',
      'bye': 'Goodbye! Wishing you a fruitful harvest.',
      'default': 'I\'m sorry, I didn\'t understand that. Could you please rephrase?'
    };

    chatForm.addEventListener('submit', function (e) {
      e.preventDefault();
      const userInput = chatInput.value.trim();
      if (userInput === '') return;
      appendMessage('user', userInput);
      chatInput.value = '';
      const botReply = getBotResponse(userInput);
      setTimeout(() => {
        appendMessage('bot', botReply);
      }, 500);
    });

    function appendMessage(sender, message) {
      const messageDiv = document.createElement('div');
      messageDiv.classList.add('message', sender);
      messageDiv.textContent = message;
      chatWindow.appendChild(messageDiv);
      chatWindow.scrollTop = chatWindow.scrollHeight;
    }

    function getBotResponse(input) {
      const lowerInput = input.toLowerCase();
      for (let key in responses) {
        if (lowerInput.includes(key)) {
          return responses[key];
        }
      }
      return responses['default'];
    }