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
      const response = await fetch('./chatbot-responses.json');
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      this.responses = data.responses || [];
      this.fallbackResponses = data.fallback_responses || [
        "I’m currently running in offline mode. You can ask me about soil health, crops, irrigation, or fertilizers."
      ];

      this.isLoaded = true;
      console.log('Chatbot responses loaded successfully');

    } catch (error) {
      console.error('Failed to load chatbot responses:', error);

      // Friendly agriculture-focused fallback
      this.responses = [];
      this.fallbackResponses = [
        "I’m currently running in offline mode. Here’s some general advice: focus on soil health, proper irrigation, and timely crop care."
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
   * Calculate Levenshtein distance
   */
  levenshteinDistance(str1, str2) {
    const matrix = Array(str2.length + 1)
      .fill(null)
      .map(() => Array(str1.length + 1).fill(null));

    for (let i = 0; i <= str1.length; i++) matrix[0][i] = i;
    for (let j = 0; j <= str2.length; j++) matrix[j][0] = j;

    for (let j = 1; j <= str2.length; j++) {
      for (let i = 1; i <= str1.length; i++) {
        const substitutionCost = str1[i - 1] === str2[j - 1] ? 0 : 1;
        matrix[j][i] = Math.min(
          matrix[j][i - 1] + 1,
          matrix[j - 1][i] + 1,
          matrix[j - 1][i - 1] + substitutionCost
        );
      }
    }

    return matrix[str2.length][str1.length];
  }

  /**
   * Check if input contains key phrases
   */
  containsKeyPhrases(input, query) {
    const inputWords = input.toLowerCase().split(/\s+/);
    const queryWords = query.toLowerCase().split(/\s+/);

    if (input.toLowerCase().includes(query.toLowerCase())) {
      return 1.0;
    }

    let matches = 0;
    for (const queryWord of queryWords) {
      if (queryWord.length > 2) {
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
   * Find best matching response
   */
  findBestMatch(userInput) {
    if (!this.isLoaded || this.responses.length === 0) {
      return this.getRandomFallback();
    }

    const input = userInput.toLowerCase().trim();
    let bestMatch = null;
    let bestScore = 0;
    const threshold = 0.4;

    for (const responseObj of this.responses) {
      const query = responseObj.query.toLowerCase();

      const exactMatch = input === query ? 1.0 : 0;
      const containsMatch = input.includes(query) || query.includes(input) ? 0.8 : 0;
      const levenshteinSimilarity = this.calculateSimilarity(input, query);
      const keyPhraseMatch = this.containsKeyPhrases(input, query);

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
   * Get random fallback response
   */
  getRandomFallback() {
    if (!Array.isArray(this.fallbackResponses) || this.fallbackResponses.length === 0) {
      return "I’m currently running in offline mode. Please ask about farming topics.";
    }
    const randomIndex = Math.floor(Math.random() * this.fallbackResponses.length);
    return this.fallbackResponses[randomIndex];
  }

  /**
   * Get response for user input
   */
  async getResponse(userInput) {
    if (!this.isLoaded) {
      await this.loadResponses();
    }
    return this.findBestMatch(userInput);
  }

  /**
   * Runtime response addition (non-persistent)
   */
  addResponse(query, response) {
    this.responses.push({ query: query.toLowerCase(), response });
  }

  /**
   * Check readiness
   */
  isReady() {
    return this.isLoaded;
  }

  /**
   * Reload responses
   */
  async reload() {
    await this.loadResponses();
  }
}

// Export globally
window.JSONChatbot = JSONChatbot;

// Node.js compatibility
if (typeof module !== 'undefined' && module.exports) {
  module.exports = JSONChatbot;
}
