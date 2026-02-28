/**
 * AgriTech API - JavaScript Fetch Examples
 * =========================================
 * Demonstrates how to call all AgriTech API endpoints
 * from a browser or Node.js frontend.
 *
 * Usage (Browser): Copy any function below into your JS file
 * Usage (Node.js): Run with `node fetch_example.js`
 *
 * GitHub: https://github.com/omroy07/AgriTech
 */

const BASE_URL = "http://localhost:5000";

// ─────────────────────────────────────────────────────────────
//  UTILITY: Generic API call wrapper with error handling
// ─────────────────────────────────────────────────────────────
async function callAPI(endpoint, method = "POST", body = null, isFormData = false) {
  const options = {
    method,
    headers: isFormData ? {} : { "Content-Type": "application/json" },
    body: body
      ? isFormData
        ? body
        : JSON.stringify(body)
      : null,
  };

  try {
    const response = await fetch(`${BASE_URL}${endpoint}`, options);
    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.error || `HTTP error ${response.status}`);
    }
    return { success: true, data };
  } catch (error) {
    if (error.name === "TypeError" && error.message.includes("fetch")) {
      return { success: false, error: "Server not running. Start with: python app.py" };
    }
    return { success: false, error: error.message };
  }
}


// ─────────────────────────────────────────────────────────────
//  1. CROP RECOMMENDATION
// ─────────────────────────────────────────────────────────────
/**
 * Get the best crop recommendation for given soil and climate data.
 *
 * @param {number} N           - Nitrogen content (kg/ha)
 * @param {number} P           - Phosphorous content (kg/ha)
 * @param {number} K           - Potassium content (kg/ha)
 * @param {number} temperature - Temperature in Celsius
 * @param {number} humidity    - Relative humidity (%)
 * @param {number} ph          - Soil pH value (0-14)
 * @param {number} rainfall    - Annual rainfall in mm
 * @returns {Promise<{crop: string, confidence: number}>}
 *
 * @example
 * const result = await predictCrop(90, 42, 43, 20.87, 82.0, 6.5, 202.93);
 * console.log(result.data.crop); // "rice"
 */
async function predictCrop(N, P, K, temperature, humidity, ph, rainfall) {
  console.log("🌾 Calling Crop Recommendation API...");
  const result = await callAPI("/predict_crop", "POST", {
    N, P, K, temperature, humidity, ph, rainfall,
  });

  if (result.success) {
    console.log(`  ✅ Recommended Crop: ${result.data.crop}`);
    console.log(`     Confidence: ${result.data.confidence}%`);
  } else {
    console.error(`  ❌ Error: ${result.error}`);
  }
  return result;
}


// ─────────────────────────────────────────────────────────────
//  2. YIELD PREDICTION
// ─────────────────────────────────────────────────────────────
/**
 * Predict crop yield in tons per hectare.
 *
 * @param {string} crop           - Crop name (e.g. "Wheat", "Rice")
 * @param {number} cropYear       - Year of cultivation
 * @param {string} season         - "Kharif" | "Rabi" | "Zaid" | "Whole Year"
 * @param {string} state          - Indian state name
 * @param {number} area           - Area in hectares
 * @param {number} annualRainfall - Annual rainfall in mm
 * @param {number} fertilizer     - Fertilizer used (kg/ha)
 * @param {number} pesticide      - Pesticide used (kg/ha)
 * @returns {Promise<{yield: number, unit: string}>}
 *
 * @example
 * const result = await predictYield("Wheat", 2024, "Rabi", "Punjab",
 *                                    1500, 750.5, 200, 15);
 * console.log(result.data.yield); // e.g. 4.2
 */
async function predictYield(crop, cropYear, season, state,
                             area, annualRainfall, fertilizer, pesticide) {
  console.log("📈 Calling Yield Prediction API...");
  const result = await callAPI("/predict_yield", "POST", {
    crop,
    crop_year:       cropYear,
    season,
    state,
    area,
    annual_rainfall: annualRainfall,
    fertilizer,
    pesticide,
  });

  if (result.success) {
    const yieldVal       = result.data.yield;
    const totalProduce   = (yieldVal * area).toFixed(1);
    console.log(`  ✅ Predicted Yield: ${yieldVal} tons/ha`);
    console.log(`     Total Produce : ${totalProduce} tons (for ${area} ha)`);
  } else {
    console.error(`  ❌ Error: ${result.error}`);
  }
  return result;
}


// ─────────────────────────────────────────────────────────────
//  3. DISEASE DETECTION (Image Upload)
// ─────────────────────────────────────────────────────────────
/**
 * Detect plant disease from a leaf image file.
 * Use with an <input type="file"> element in the browser.
 *
 * @param {File} imageFile - File object from input[type=file]
 * @returns {Promise<{disease: string, confidence: number,
 *                    is_healthy: boolean, treatment: string}>}
 *
 * @example
 * // HTML: <input type="file" id="leafImage" accept="image/*">
 * const input = document.getElementById("leafImage");
 * input.addEventListener("change", async () => {
 *   const result = await detectDisease(input.files[0]);
 *   console.log(result.data.disease);
 * });
 */
async function detectDisease(imageFile) {
  console.log("🌿 Calling Disease Detection API...");

  if (!imageFile) {
    return { success: false, error: "No image file provided" };
  }

  const formData = new FormData();
  formData.append("file", imageFile);

  const result = await callAPI("/predict_disease", "POST", formData, true);

  if (result.success) {
    const status = result.data.is_healthy ? "Healthy ✅" : "Diseased ⚠️";
    console.log(`  ✅ Status    : ${status}`);
    console.log(`     Disease  : ${result.data.disease}`);
    console.log(`     Confidence: ${result.data.confidence}%`);
    console.log(`     Treatment: ${result.data.treatment}`);
  } else {
    console.error(`  ❌ Error: ${result.error}`);
  }
  return result;
}


// ─────────────────────────────────────────────────────────────
//  4. FERTILIZER RECOMMENDATION
// ─────────────────────────────────────────────────────────────
/**
 * Get fertilizer recommendation for given soil and crop conditions.
 *
 * @param {number} temperature  - Soil temperature (Celsius)
 * @param {number} humidity     - Humidity (%)
 * @param {number} moisture     - Soil moisture (%)
 * @param {string} soilType     - "Sandy"|"Loamy"|"Black"|"Red"|"Clayey"
 * @param {string} cropType     - Crop name (e.g. "Maize", "Cotton")
 * @param {number} nitrogen     - Current N level in soil
 * @param {number} potassium    - Current K level in soil
 * @param {number} phosphorous  - Current P level in soil
 * @returns {Promise<{fertilizer: string, recommendation: string}>}
 *
 * @example
 * const result = await recommendFertilizer(26, 52, 38, "Sandy", "Maize", 37, 0, 0);
 * console.log(result.data.fertilizer); // e.g. "Urea"
 */
async function recommendFertilizer(temperature, humidity, moisture,
                                    soilType, cropType,
                                    nitrogen, potassium, phosphorous) {
  console.log("🧪 Calling Fertilizer Recommendation API...");
  const result = await callAPI("/predict_fertilizer", "POST", {
    Temperature:  temperature,
    Humidity:     humidity,
    Moisture:     moisture,
    "Soil Type":  soilType,
    "Crop Type":  cropType,
    Nitrogen:     nitrogen,
    Potassium:    potassium,
    Phosphorous:  phosphorous,
  });

  if (result.success) {
    console.log(`  ✅ Fertilizer     : ${result.data.fertilizer}`);
    console.log(`     Recommendation : ${result.data.recommendation}`);
  } else {
    console.error(`  ❌ Error: ${result.error}`);
  }
  return result;
}


// ─────────────────────────────────────────────────────────────
//  5. SOIL CLASSIFICATION (Image Upload)
// ─────────────────────────────────────────────────────────────
/**
 * Classify soil type from an image.
 *
 * @param {File} soilImageFile - File object from input[type=file]
 * @returns {Promise<{soil_type: string, confidence: number,
 *                    properties: object}>}
 *
 * @example
 * const result = await classifySoil(soilInput.files[0]);
 * console.log(result.data.soil_type); // e.g. "Black Cotton Soil"
 */
async function classifySoil(soilImageFile) {
  console.log("🪨 Calling Soil Classification API...");

  if (!soilImageFile) {
    return { success: false, error: "No soil image file provided" };
  }

  const formData = new FormData();
  formData.append("file", soilImageFile);

  const result = await callAPI("/classify_soil", "POST", formData, true);

  if (result.success) {
    console.log(`  ✅ Soil Type  : ${result.data.soil_type}`);
    console.log(`     Confidence: ${result.data.confidence}%`);
    if (result.data.properties) {
      console.log(`     Properties:`, result.data.properties);
    }
  } else {
    console.error(`  ❌ Error: ${result.error}`);
  }
  return result;
}


// ─────────────────────────────────────────────────────────────
//  6. CROP PRICE TRACKER
// ─────────────────────────────────────────────────────────────
/**
 * Get current market prices for a specific crop.
 *
 * @param {string} cropName - Crop name (e.g. "Wheat", "Rice")
 * @param {string} state    - State name (optional)
 * @returns {Promise<{crop: string, price: number, unit: string,
 *                    market: string, date: string}>}
 *
 * @example
 * const result = await getCropPrice("Wheat", "Punjab");
 * console.log(`Price: ₹${result.data.price} per quintal`);
 */
async function getCropPrice(cropName, state = "") {
  console.log("💰 Calling Crop Price Tracker API...");
  const result = await callAPI("/crop_price", "GET", null);

  if (result.success) {
    console.log(`  ✅ ${cropName}: ₹${result.data.price} per ${result.data.unit}`);
  } else {
    console.error(`  ❌ Error: ${result.error}`);
  }
  return result;
}


// ─────────────────────────────────────────────────────────────
//  7. COMPLETE HTML INTEGRATION EXAMPLE
// ─────────────────────────────────────────────────────────────
/**
 * Full HTML form handler example.
 * Copy this into your HTML page.
 *
 * @example
 * <!-- HTML -->
 * <form id="cropForm">
 *   <input id="nitrogen"     type="number" placeholder="Nitrogen">
 *   <input id="phosphorous"  type="number" placeholder="Phosphorous">
 *   <input id="potassium"    type="number" placeholder="Potassium">
 *   <input id="temperature"  type="number" placeholder="Temperature">
 *   <input id="humidity"     type="number" placeholder="Humidity">
 *   <input id="ph"           type="number" placeholder="pH" step="0.1">
 *   <input id="rainfall"     type="number" placeholder="Rainfall">
 *   <button type="button" onclick="handleCropFormSubmit()">
 *     Get Recommendation
 *   </button>
 * </form>
 * <div id="cropResult"></div>
 */
async function handleCropFormSubmit() {
  const getValue = (id) => parseFloat(document.getElementById(id).value);

  const N           = getValue("nitrogen");
  const P           = getValue("phosphorous");
  const K           = getValue("potassium");
  const temperature = getValue("temperature");
  const humidity    = getValue("humidity");
  const ph          = getValue("ph");
  const rainfall    = getValue("rainfall");

  // Show loading state
  const resultDiv = document.getElementById("cropResult");
  if (resultDiv) resultDiv.innerHTML = "<p>⏳ Predicting...</p>";

  const result = await predictCrop(N, P, K, temperature, humidity, ph, rainfall);

  if (resultDiv) {
    if (result.success) {
      resultDiv.innerHTML = `
        <div class="result-card">
          <h3>🌾 Recommended Crop</h3>
          <p class="crop-name">${result.data.crop.toUpperCase()}</p>
          <p class="confidence">Confidence: ${result.data.confidence}%</p>
        </div>`;
    } else {
      resultDiv.innerHTML = `<p class="error">❌ ${result.error}</p>`;
    }
  }
}


// ─────────────────────────────────────────────────────────────
//  8. DEMO - Run all API calls (Node.js)
// ─────────────────────────────────────────────────────────────
async function runAllDemos() {
  console.log("=".repeat(55));
  console.log("   🌾 AgriTech API - JavaScript Fetch Examples");
  console.log("=".repeat(55));

  // 1. Crop Recommendation
  console.log("\n[1/4] CROP RECOMMENDATION");
  await predictCrop(90, 42, 43, 20.87, 82.0, 6.5, 202.93);

  // 2. Yield Prediction
  console.log("\n[2/4] YIELD PREDICTION");
  await predictYield("Wheat", 2024, "Rabi", "Punjab", 1500, 750.5, 200, 15);

  // 3. Fertilizer Recommendation
  console.log("\n[3/4] FERTILIZER RECOMMENDATION");
  await recommendFertilizer(26, 52, 38, "Sandy", "Maize", 37, 0, 0);

  // 4. Crop Price
  console.log("\n[4/4] CROP PRICE TRACKER");
  await getCropPrice("Wheat", "Punjab");

  console.log("\n" + "=".repeat(55));
  console.log("   Note: Disease detection requires a File object (browser only)");
  console.log("   Start the server: cd AgriTech && python app.py");
  console.log("=".repeat(55));
}

// ─────────────────────────────────────────────────────────────
//  EXPORT (for use as a module in Node.js or bundlers)
// ─────────────────────────────────────────────────────────────
if (typeof module !== "undefined" && module.exports) {
  module.exports = {
    predictCrop,
    predictYield,
    detectDisease,
    recommendFertilizer,
    classifySoil,
    getCropPrice,
    handleCropFormSubmit,
    runAllDemos,
  };

  // Auto-run demos when executed directly: node fetch_example.js
  runAllDemos().catch(console.error);
}
