/**
 * Crop domain schema
 * Shared across roadmap, prediction, and analytics
 */

export const CropSchema = {
  type: "object",
  required: ["id", "name", "durationDays"],
  properties: {
    id: {
      type: "string",
      description: "Unique crop identifier"
    },
    name: {
      type: "string",
      description: "Human readable crop name"
    },
    durationDays: {
      type: "number",
      description: "Total crop lifecycle in days"
    }
  }
};