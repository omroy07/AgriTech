// static/script.js

document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const form = document.getElementById('crop-form');
    const resultContainer = document.getElementById('result-container');
    const resultText = document.getElementById('result-text');
    const guideContainer = document.getElementById('guide-container');
    const guideTitle = document.getElementById('guide-title');
    const guideTimeline = document.getElementById('guide-timeline');
    const guideHowToPlant = document.getElementById('guide-how-to-plant');
    const guideFertilizer = document.getElementById('guide-fertilizer');
    const guideIdealRainfall = document.getElementById('guide-ideal-rainfall');
    const guidePostHarvest = document.getElementById('guide-post-harvest');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const formData = new FormData(form);
        const data = {};
        formData.forEach((value, key) => {
            const el = document.getElementsByName(key)[0];
            data[key] = el.type === 'number' ? parseFloat(value) : value;
        });

        // Show loading message
        displayLoading();

        // Generate a prompt for the Gemini API
        const prompt = `Act as an expert agricultural AI. Based on the following farm conditions, recommend the best crop and provide a detailed farming guide.
        - Soil pH: ${data.pH}
        - Temperature: ${data.Temperature}°C
        - Rainfall: ${data.Rainfall} mm
        - Soil Type: ${data.Soil_Type}
        - Season: ${data.Season}
        - Market Demand: ${data.Market_Demand}
        - Fertilizer Used: ${data.Fertilizer_Used}
        - Pest Issue: ${data.Pest_Issue}
        - Irrigation Method: ${data.Irrigation_Method}

        Provide the response in a JSON format with the following schema. Use natural language and markdown formatting (like **bold** or lists) where appropriate for readability.
        
        {
          "crop": "Recommended Crop Name",
          "guide": {
            "title": "Farming Guide for [Crop Name]",
            "timeline": "Detailed timeline (e.g., planting season, harvest time).",
            "how_to_plant": "Step-by-step instructions on how to plant the crop.",
            "fertilizer": "A plan for fertilizer application.",
            "ideal_rainfall": "The ideal rainfall amount and schedule.",
            "post_harvest": "Instructions for post-harvest care and storage."
          }
        }
        `;

        try {
            // Make the API call to Gemini
            const result = await generateContentWithRetry(prompt);
            
            // Check for valid response structure
            if (result && result.crop && result.guide) {
                displayResultAndGuide(result.crop, result.guide);
            } else {
                displayError("Failed to get a valid response from the AI. Please try again.");
            }
        } catch (error) {
            console.error("Error calling Gemini API:", error);
            displayError("Could not connect to the AI service. Please check your network connection.");
        }
    });

    /**
     * Calls the Gemini API with exponential backoff.
     * @param {string} prompt The text prompt for the model.
     * @returns {Promise<object>} The parsed JSON response.
     */
    async function generateContentWithRetry(prompt, retries = 3, delay = 1000) {
        let chatHistory = [{ role: "user", parts: [{ text: prompt }] }];
        const payload = {
            contents: chatHistory,
            generationConfig: {
                responseMimeType: "application/json",
                responseSchema: {
                    type: "OBJECT",
                    properties: {
                        "crop": { "type": "STRING" },
                        "guide": {
                            "type": "OBJECT",
                            "properties": {
                                "title": { "type": "STRING" },
                                "timeline": { "type": "STRING" },
                                "how_to_plant": { "type": "STRING" },
                                "fertilizer": { "type": "STRING" },
                                "ideal_rainfall": { "type": "STRING" },
                                "post_harvest": { "type": "STRING" }
                            }
                        }
                    }
                }
            }
        };

        const apiKey = "";
        const apiUrl = `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-05-20:generateContent?key=${apiKey}`;

        for (let i = 0; i < retries; i++) {
            try {
                const response = await fetch(apiUrl, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });

                if (response.status === 429 && i < retries - 1) {
                    await new Promise(res => setTimeout(res, delay));
                    delay *= 2; // Exponential backoff
                    continue;
                }

                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(`API error: ${JSON.stringify(errorData)}`);
                }

                const result = await response.json();
                const jsonText = result?.candidates?.[0]?.content?.parts?.[0]?.text;
                if (!jsonText) {
                    throw new Error("Invalid response format from API.");
                }

                return JSON.parse(jsonText);

            } catch (error) {
                if (i === retries - 1) {
                    console.error("Failed to generate content after multiple retries:", error);
                    throw error;
                }
            }
        }
    }

    /**
     * Displays a loading message in the result container.
     */
    function displayLoading() {
        resultContainer.classList.remove('hidden');
        resultText.textContent = 'Curating your personalized crop guide...';
        guideContainer.classList.add('hidden');
    }

    /**
     * Displays an error message in the result container.
     * @param {string} message The error message to display.
     */
    function displayError(message) {
        resultContainer.classList.remove('hidden');
        resultText.textContent = message;
        guideContainer.classList.add('hidden');
    }

    /**
     * Simple function to convert basic markdown (like **bold**) to HTML.
     * @param {string} text The text to format.
     * @returns {string} The formatted HTML string.
     */
    function formatAIResponse(text) {
        if (!text) return '';
        // Convert **bold** to <strong>bold</strong>
        let formattedText = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        // Convert newlines to <br> tags for multi-line content
        formattedText = formattedText.replace(/\n/g, '<br>');
        return formattedText;
    }

    /**
     * Populates the result and guide sections with the API response.
     * @param {string} cropName The recommended crop name.
     * @param {object} guide The guide object from the API response.
     */
    function displayResultAndGuide(cropName, guide) {
        resultContainer.classList.remove('hidden');
        resultText.textContent = cropName;

        guideTitle.textContent = guide.title;
        
        // Use the new formatting function and .innerHTML
        guideTimeline.innerHTML = formatAIResponse(guide.timeline);
        guideHowToPlant.innerHTML = formatAIResponse(guide.how_to_plant);
        guideFertilizer.innerHTML = formatAIResponse(guide.fertilizer);
        guideIdealRainfall.innerHTML = formatAIResponse(guide.ideal_rainfall);
        guidePostHarvest.innerHTML = formatAIResponse(guide.post_harvest);
        
        guideContainer.classList.remove('hidden');
    }
});
