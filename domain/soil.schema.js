/**
 * Soil data schema
 */

export const SoilDataSchema = {
  type: "object",
  required: ["ph", "moisture"],
  properties: {
    ph: {
      type: "number",
      description: "Soil pH value"
    },
    moisture: {
      type: "number",
      description: "Soil moisture percentage"
    }
  }
};