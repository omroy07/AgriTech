/**
 * Growth stage schema
 */

export const GrowthStageSchema = {
  type: "object",
  required: ["name", "startDay", "endDay"],
  properties: {
    name: {
      type: "string",
      description: "Stage name (e.g., Germination)"
    },
    startDay: {
      type: "number",
      description: "Start day of stage"
    },
    endDay: {
      type: "number",
      description: "End day of stage"
    }
  }
};