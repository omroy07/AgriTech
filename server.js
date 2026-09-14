const express = require('express');
const cors = require('cors');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 3000;

const API_KEY = process.env.GEMINI_API_KEY;
const API_URL = `https://generativelanguage.googleapis.com/v1/models/gemini-2.5-flash:generateContent?key=${API_KEY}`;

if (!API_KEY) {
  console.warn('⚠️ GEMINI_API_KEY not found. AI features will be limited. Using rule-based responses only.');
}

app.use(cors());
app.use(express.json({ limit: '5mb' }));

app.post('/api/chat', async (req, res) => {
  const { message, image } = req.body;

  if (!message && !image) {
    return res.status(400).json({ error: 'Message or image required' });
  }

  try {
    // If no API key, return a helpful message about using the JSON chatbot
    if (!API_KEY) {
      return res.json({
        reply: "🤖 I'm currently running in offline mode. For AI-powered responses, please configure your GEMINI_API_KEY. Meanwhile, try our rule-based chatbot at /chat for instant farming advice!"
      });
    }

    const agriculturalVisionPrompt = image 
      ? `You are AgriBot, an expert agricultural AI specialist. The user has provided an image of a plant, crop, or leaf.
${message ? `User's question/note: "${message}"` : 'Please analyze this image.'}

Provide a structured response:
1. 🌿 **Crop Identification**: Identify the crop/plant.
2. 🔍 **Condition / Diagnosis**: Identify any visible disease (e.g. blight, rust, leaf spot, mildew), pest infestation, or nutrient deficiency.
3. 💊 **Recommended Remedies**: Provide step-by-step practical remedies (both Organic / Bio-control and Chemical solutions suitable for Indian agriculture).
4. 🛡️ **Preventive Measures**: How to prevent recurrence (irrigation, crop rotation, soil care).
Keep the advice clear, friendly, and practical for farmers.`
      : (message || 'Please provide agriculture advice.');

    const payload = {
      contents: [
        {
          role: 'user',
          parts: [
            { text: agriculturalVisionPrompt },
            ...(image
              ? [{
                  inline_data: {
                    mime_type: 'image/jpeg',
                    data: image
                  }
                }]
              : [])
          ]
        }
      ],
      generationConfig: {
        temperature: 0.5,
        maxOutputTokens: 1000
      }
    };

    const response = await fetch(API_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    if (!response.ok) {
      const errText = await response.text();
      console.error('API Error:', errText);
      return res.status(500).json({ reply: '⚠️ AI service temporarily unavailable. Please try our rule-based chatbot for instant farming advice!' });
    }

    const data = await response.json();

    const reply =
      data?.candidates?.[0]?.content?.parts?.map(p => p.text)?.join('') ||
      "I couldn't analyze that. Please try again.";

    res.json({ reply });
  } catch (err) {
    console.error('Server Error:', err);
    res.status(500).json({ reply: '⚠️ Server error. Please try our rule-based chatbot for instant farming advice!' });
  }
});

app.use(express.static('.'));

app.listen(PORT, () => {
  console.log(`🚀 AgriTech Chatbot Server running on http://localhost:${PORT}`);
  console.log(`🤖 AI Features: ${API_KEY ? 'ENABLED' : 'DISABLED (using fallback mode)'}`);
});


