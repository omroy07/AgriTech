/**
 * Prediction output schema
 */

export const PredictionResultSchema = {
  type: "object",
  required: ["confidence", "result"],
  properties: {
    confidence: {
      type: "number",
      description: "Model confidence score (0–1)"
    },
    result: {
      type: "string",
      description: "Prediction outcome"
    }
  }
};