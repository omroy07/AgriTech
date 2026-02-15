/**
 * AgriTech JSON-based Chatbot Module
 * Provides intelligent response matching with fuzzy search capabilities
 */

class JSONChatbot {
  constructor() {
    this.responses = [];
    this.fallbackResponses = [];
    this.isLoaded = false;
    this.loadResponses();
  }

  /**
   * Load responses from JSON file
   */
  async loadResponses() {
    try {
      const response = await fetch(`${APP_CONFIG.API_BASE_URL}/api/chatbot-responses.json`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      this.responses = data.responses || [];
      this.fallbackResponses = data.fallback_responses || [
        "Sorry, I didn't understand that. Could you ask about farming topics?"
      ];
      this.isLoaded = true;
      console.log('✅ Chatbot responses loaded successfully');
    } catch (error) {
      console.error('❌ Failed to load chatbot responses:', error);
      this.responses = [];
      this.fallbackResponses = [
        "I'm having trouble accessing my knowledge base. Please try asking about general farming topics!"
      ];
      this.isLoaded = false;
    }
  }

  /**
   * Calculate similarity between two strings using Levenshtein distance
   */
  calculateSimilarity(str1, str2) {
    str1 = str1.toLowerCase().trim();
    str2 = str2.toLowerCase().trim();
    
    if (str1 === str2) return 1.0;
    
    const longer = str1.length > str2.length ? str1 : str2;
    const shorter = str1.length > str2.length ? str2 : str1;
    
    if (longer.length === 0) return 1.0;
    
    const distance = this.levenshteinDistance(longer, shorter);
    return (longer.length - distance) / longer.length;
  }

  /**
   * Calculate Levenshtein distance between two strings
   */
  levenshteinDistance(str1, str2) {
    const matrix = Array(str2.length + 1).fill(null).map(() => Array(str1.length + 1).fill(null));
    
    for (let i = 0; i <= str1.length; i++) matrix[0][i] = i;
    for (let j = 0; j <= str2.length; j++) matrix[j][0] = j;
    
    for (let j = 1; j <= str2.length; j++) {
      for (let i = 1; i <= str1.length; i++) {
        const substitutionCost = str1[i - 1] === str2[j - 1] ? 0 : 1;
        matrix[j][i] = Math.min(
          matrix[j][i - 1] + 1, // insertion
          matrix[j - 1][i] + 1, // deletion
          matrix[j - 1][i - 1] + substitutionCost // substitution
        );
      }
    }
    
    return matrix[str2.length][str1.length];
  }

  /**
   * Check if input contains key phrases from the query
   */
  containsKeyPhrases(input, query) {
    const inputWords = input.toLowerCase().split(/\s+/);
    const queryWords = query.toLowerCase().split(/\s+/);
    
    // Check for exact phrase match
    if (input.toLowerCase().includes(query.toLowerCase())) {
      return 1.0;
    }
    
    // Check for word matches
    let matches = 0;
    for (const queryWord of queryWords) {
      if (queryWord.length > 2) { // Ignore short words
        for (const inputWord of inputWords) {
          if (inputWord.includes(queryWord) || queryWord.includes(inputWord)) {
            matches++;
            break;
          }
        }
      }
    }
    
    return queryWords.length > 0 ? matches / queryWords.length : 0;
  }

  /**
   * Find the best matching response for user input
   */
  findBestMatch(userInput) {
    if (!this.isLoaded || this.responses.length === 0) {
      return this.getRandomFallback();
    }

    const input = userInput.toLowerCase().trim();
    let bestMatch = null;
    let bestScore = 0;
    const threshold = 0.4; // Minimum similarity threshold

    for (const responseObj of this.responses) {
      const query = responseObj.query.toLowerCase();
      
      // Calculate multiple similarity metrics
      const exactMatch = input === query ? 1.0 : 0;
      const containsMatch = input.includes(query) || query.includes(input) ? 0.8 : 0;
      const levenshteinSimilarity = this.calculateSimilarity(input, query);
      const keyPhraseMatch = this.containsKeyPhrases(input, query);
      
      // Weighted score combining different matching methods
      const score = Math.max(
        exactMatch,
        containsMatch,
        levenshteinSimilarity * 0.7,
        keyPhraseMatch * 0.6
      );

      if (score > bestScore && score >= threshold) {
        bestScore = score;
        bestMatch = responseObj;
      }
    }

    return bestMatch ? bestMatch.response : this.getRandomFallback();
  }

  /**
   * Get a random fallback response
   * (Fixed: Handles empty or undefined fallbackResponses gracefully)
   */
  getRandomFallback() {
    if (!Array.isArray(this.fallbackResponses) || this.fallbackResponses.length === 0) {
      return "Sorry, I didn't understand that.";
    }
    const randomIndex = Math.floor(Math.random() * this.fallbackResponses.length);
    return this.fallbackResponses[randomIndex];
  }

  /**
   * Get response for user input
   */
  async getResponse(userInput) {
    // Wait for responses to load if they haven't already
    if (!this.isLoaded) {
      await this.loadResponses();
    }
    
    const response = this.findBestMatch(userInput);
    return response;
  }

  /**
   * Add new response to the system (runtime only, doesn't persist)
   */
  addResponse(query, response) {
    this.responses.push({ query: query.toLowerCase(), response });
    console.log('✅ Added new response for:', query);
  }

  /**
   * Get all available queries (for debugging/admin purposes)
   */
  getAllQueries() {
    return this.responses.map(r => r.query);
  }

  /**
   * Check if chatbot is ready
   */
  isReady() {
    return this.isLoaded;
  }

  /**
   * Reload responses from JSON file
   */
  async reload() {
    console.log('🔄 Reloading chatbot responses...');
    await this.loadResponses();
  }
}

// Create and export chatbot instance
window.JSONChatbot = JSONChatbot;

// For Node.js compatibility
if (typeof module !== 'undefined' && module.exports) {
  module.exports = JSONChatbot;
}