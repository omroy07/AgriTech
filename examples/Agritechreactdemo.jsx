/**
 * AgriTech - React Frontend Integration Example
 * ===============================================
 * A complete React component showing how to integrate
 * with the AgriTech Flask API from a React frontend.
 *
 * Features demonstrated:
 *  - Crop Recommendation form
 *  - Disease Detection image upload
 *  - Yield Prediction form
 *  - Fertilizer Recommendation form
 *  - Error handling and loading states
 *
 * Usage:
 *   1. Copy this file into your React project's src/components/
 *   2. Import and render: <AgriTechDemo />
 *   3. Make sure the Flask server is running on port 5000
 *
 * GitHub: https://github.com/omroy07/AgriTech
 */

import React, { useState } from "react";

const BASE_URL = "http://localhost:5000";

// ─────────────────────────────────────────────────────────────
//  API CALLS
// ─────────────────────────────────────────────────────────────
async function apiPost(endpoint, body, isFormData = false) {
  const res = await fetch(`${BASE_URL}${endpoint}`, {
    method: "POST",
    headers: isFormData ? {} : { "Content-Type": "application/json" },
    body: isFormData ? body : JSON.stringify(body),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.error || `HTTP ${res.status}`);
  return data;
}


// ─────────────────────────────────────────────────────────────
//  CROP RECOMMENDATION COMPONENT
// ─────────────────────────────────────────────────────────────
function CropRecommendation() {
  const [form, setForm] = useState({
    N: 90, P: 42, K: 43,
    temperature: 20.87, humidity: 82.0,
    ph: 6.5, rainfall: 202.93,
  });
  const [result, setResult]   = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError]     = useState(null);

  const handleChange = (e) =>
    setForm({ ...form, [e.target.name]: parseFloat(e.target.value) });

  const handleSubmit = async () => {
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const data = await apiPost("/predict_crop", form);
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const fields = [
    { name: "N",           label: "Nitrogen (kg/ha)",     step: "1"   },
    { name: "P",           label: "Phosphorous (kg/ha)",  step: "1"   },
    { name: "K",           label: "Potassium (kg/ha)",    step: "1"   },
    { name: "temperature", label: "Temperature (°C)",      step: "0.1" },
    { name: "humidity",    label: "Humidity (%)",          step: "0.1" },
    { name: "ph",          label: "Soil pH",               step: "0.01"},
    { name: "rainfall",    label: "Rainfall (mm)",         step: "0.1" },
  ];

  return (
    <div style={styles.card}>
      <h2 style={styles.cardTitle}>🌾 Crop Recommendation</h2>
      <div style={styles.grid}>
        {fields.map(({ name, label, step }) => (
          <div key={name} style={styles.field}>
            <label style={styles.label}>{label}</label>
            <input
              type="number"
              name={name}
              value={form[name]}
              step={step}
              onChange={handleChange}
              style={styles.input}
            />
          </div>
        ))}
      </div>

      <button onClick={handleSubmit} disabled={loading} style={styles.button}>
        {loading ? "⏳ Predicting..." : "🔍 Get Recommendation"}
      </button>

      {error && <div style={styles.error}>❌ {error}</div>}

      {result && (
        <div style={styles.result}>
          <div style={styles.resultTitle}>✅ Recommended Crop</div>
          <div style={styles.cropName}>{result.crop?.toUpperCase()}</div>
          {result.confidence && (
            <div style={styles.confidence}>
              Confidence: {result.confidence}%
            </div>
          )}
        </div>
      )}
    </div>
  );
}


// ─────────────────────────────────────────────────────────────
//  DISEASE DETECTION COMPONENT
// ─────────────────────────────────────────────────────────────
function DiseaseDetection() {
  const [imageFile, setImageFile]   = useState(null);
  const [preview, setPreview]       = useState(null);
  const [result, setResult]         = useState(null);
  const [loading, setLoading]       = useState(false);
  const [error, setError]           = useState(null);

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setImageFile(file);
    setPreview(URL.createObjectURL(file));
    setResult(null);
    setError(null);
  };

  const handleDetect = async () => {
    if (!imageFile) { setError("Please select a leaf image first."); return; }
    setLoading(true);
    setError(null);
    try {
      const formData = new FormData();
      formData.append("file", imageFile);
      const data = await apiPost("/predict_disease", formData, true);
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={styles.card}>
      <h2 style={styles.cardTitle}>🌿 Disease Detection</h2>

      <div style={styles.uploadArea}>
        <input
          type="file"
          accept="image/*"
          onChange={handleFileChange}
          style={{ display: "none" }}
          id="leafUpload"
        />
        <label htmlFor="leafUpload" style={styles.uploadLabel}>
          {preview ? "📷 Change Image" : "📤 Upload Leaf Image"}
        </label>

        {preview && (
          <img
            src={preview}
            alt="Leaf preview"
            style={styles.imagePreview}
          />
        )}
      </div>

      <button onClick={handleDetect} disabled={loading || !imageFile}
              style={styles.button}>
        {loading ? "⏳ Analyzing..." : "🔬 Detect Disease"}
      </button>

      {error && <div style={styles.error}>❌ {error}</div>}

      {result && (
        <div style={{
          ...styles.result,
          borderColor: result.is_healthy ? "#2E8B57" : "#CC3300",
        }}>
          <div style={styles.resultTitle}>
            {result.is_healthy ? "✅ Healthy Plant" : "⚠️ Disease Detected"}
          </div>
          <p><strong>Diagnosis:</strong> {result.disease}</p>
          <p><strong>Confidence:</strong> {result.confidence}%</p>
          <p><strong>Treatment:</strong> {result.treatment}</p>
        </div>
      )}
    </div>
  );
}


// ─────────────────────────────────────────────────────────────
//  YIELD PREDICTION COMPONENT
// ─────────────────────────────────────────────────────────────
function YieldPrediction() {
  const [form, setForm] = useState({
    crop: "Wheat", crop_year: 2024, season: "Rabi",
    state: "Punjab", area: 1500,
    annual_rainfall: 750.5, fertilizer: 200, pesticide: 15,
  });
  const [result, setResult]   = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError]     = useState(null);

  const handleChange = (e) => {
    const val = isNaN(e.target.value) ? e.target.value : parseFloat(e.target.value);
    setForm({ ...form, [e.target.name]: val });
  };

  const handleSubmit = async () => {
    setLoading(true); setError(null); setResult(null);
    try {
      const data = await apiPost("/predict_yield", form);
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={styles.card}>
      <h2 style={styles.cardTitle}>📈 Yield Prediction</h2>

      <div style={styles.grid}>
        {[
          { name: "crop",            label: "Crop Name",        type: "text"   },
          { name: "crop_year",       label: "Year",             type: "number" },
          { name: "area",            label: "Area (ha)",        type: "number" },
          { name: "annual_rainfall", label: "Rainfall (mm)",    type: "number" },
          { name: "fertilizer",      label: "Fertilizer (kg/ha)", type: "number"},
          { name: "pesticide",       label: "Pesticide (kg/ha)", type: "number"},
        ].map(({ name, label, type }) => (
          <div key={name} style={styles.field}>
            <label style={styles.label}>{label}</label>
            <input
              type={type}
              name={name}
              value={form[name]}
              onChange={handleChange}
              style={styles.input}
            />
          </div>
        ))}

        <div style={styles.field}>
          <label style={styles.label}>Season</label>
          <select name="season" value={form.season}
                  onChange={handleChange} style={styles.input}>
            {["Kharif","Rabi","Zaid","Whole Year","Autumn","Summer","Winter"]
              .map(s => <option key={s}>{s}</option>)}
          </select>
        </div>

        <div style={styles.field}>
          <label style={styles.label}>State</label>
          <input type="text" name="state" value={form.state}
                 onChange={handleChange} style={styles.input} />
        </div>
      </div>

      <button onClick={handleSubmit} disabled={loading} style={styles.button}>
        {loading ? "⏳ Predicting..." : "📊 Predict Yield"}
      </button>

      {error && <div style={styles.error}>❌ {error}</div>}

      {result && (
        <div style={styles.result}>
          <div style={styles.resultTitle}>📈 Yield Prediction</div>
          <p><strong>Yield:</strong> {result.yield} tons/ha</p>
          <p><strong>Total for {form.area} ha:</strong>
            {(result.yield * form.area).toFixed(1)} tons</p>
        </div>
      )}
    </div>
  );
}


// ─────────────────────────────────────────────────────────────
//  MAIN DEMO COMPONENT
// ─────────────────────────────────────────────────────────────
const TABS = [
  { id: "crop",    label: "🌾 Crop",    Component: CropRecommendation },
  { id: "disease", label: "🌿 Disease", Component: DiseaseDetection  },
  { id: "yield",   label: "📈 Yield",   Component: YieldPrediction   },
];

export default function AgriTechDemo() {
  const [activeTab, setActiveTab] = useState("crop");
  const ActiveComponent = TABS.find(t => t.id === activeTab)?.Component;

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <h1 style={styles.title}>🌾 AgriTech Demo</h1>
        <p style={styles.subtitle}>
          AI-powered farming tools | Server: {BASE_URL}
        </p>
      </div>

      {/* Tab Bar */}
      <div style={styles.tabBar}>
        {TABS.map(({ id, label }) => (
          <button
            key={id}
            onClick={() => setActiveTab(id)}
            style={{
              ...styles.tab,
              ...(activeTab === id ? styles.tabActive : {}),
            }}
          >
            {label}
          </button>
        ))}
      </div>

      {/* Active Component */}
      {ActiveComponent && <ActiveComponent />}

      <p style={styles.footer}>
        GitHub:{" "}
        <a href="https://github.com/omroy07/AgriTech"
           target="_blank" rel="noreferrer">
          omroy07/AgriTech
        </a>
      </p>
    </div>
  );
}


// ─────────────────────────────────────────────────────────────
//  STYLES
// ─────────────────────────────────────────────────────────────
const styles = {
  container:    { maxWidth: 680, margin: "0 auto", padding: "20px", fontFamily: "sans-serif" },
  header:       { textAlign: "center", marginBottom: 20 },
  title:        { fontSize: 28, color: "#2E8B57", margin: 0 },
  subtitle:     { color: "#666", margin: "4px 0 0" },
  tabBar:       { display: "flex", gap: 8, marginBottom: 20 },
  tab:          { flex: 1, padding: "10px 8px", border: "2px solid #2E8B57",
                  background: "#fff", color: "#2E8B57", borderRadius: 8,
                  cursor: "pointer", fontWeight: 600, fontSize: 14 },
  tabActive:    { background: "#2E8B57", color: "#fff" },
  card:         { background: "#fff", border: "1px solid #ddd", borderRadius: 12,
                  padding: 24, boxShadow: "0 2px 8px rgba(0,0,0,0.07)" },
  cardTitle:    { fontSize: 20, color: "#2E8B57", marginTop: 0 },
  grid:         { display: "grid", gridTemplateColumns: "1fr 1fr", gap: "12px 20px" },
  field:        { display: "flex", flexDirection: "column" },
  label:        { fontSize: 12, color: "#555", marginBottom: 4, fontWeight: 600 },
  input:        { padding: "8px 10px", border: "1px solid #ccc", borderRadius: 6,
                  fontSize: 14, outline: "none" },
  button:       { marginTop: 20, width: "100%", padding: "12px",
                  background: "#2E8B57", color: "#fff", border: "none",
                  borderRadius: 8, fontSize: 15, cursor: "pointer", fontWeight: 600 },
  result:       { marginTop: 16, padding: 16, background: "#f0fff4",
                  border: "2px solid #2E8B57", borderRadius: 8 },
  resultTitle:  { fontWeight: 700, fontSize: 16, marginBottom: 8 },
  cropName:     { fontSize: 28, fontWeight: 800, color: "#2E8B57" },
  confidence:   { color: "#555", marginTop: 4 },
  error:        { marginTop: 12, padding: 12, background: "#fff0f0",
                  border: "1px solid #ff4444", borderRadius: 8, color: "#cc0000" },
  uploadArea:   { display: "flex", flexDirection: "column", alignItems: "center", gap: 12 },
  uploadLabel:  { padding: "12px 24px", background: "#e8f5e9", border: "2px dashed #2E8B57",
                  borderRadius: 8, cursor: "pointer", color: "#2E8B57", fontWeight: 600 },
  imagePreview: { maxWidth: "100%", maxHeight: 200, borderRadius: 8, objectFit: "cover" },
  footer:       { textAlign: "center", marginTop: 20, color: "#999", fontSize: 13 },
};
