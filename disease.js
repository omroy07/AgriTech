const diseaseDatabase = {
  Tomato___Bacterial_spot: {
    name: "Tomato Bacterial Spot",
    severity: "high",
    description:
      "Bacterial infection causing small, dark spots on leaves, stems, and fruit. Spreads rapidly in warm, humid conditions.",
    treatment:
      "Apply copper-based bactericides at first sign of disease. Improve air circulation, avoid overhead watering, remove infected plant debris, and consider disease-resistant varieties.",
  },
  Tomato___Early_blight: {
    name: "Tomato Early Blight",
    severity: "medium",
    description:
      "Fungal disease causing dark spots with concentric rings on older leaves. Can reduce yield significantly if left untreated.",
    treatment:
      "Apply fungicides containing chlorothalonil or copper. Remove affected lower leaves, ensure proper plant spacing, and mulch to prevent soil splash.",
  },
  Tomato___Late_blight: {
    name: "Tomato Late Blight",
    severity: "high",
    description:
      "Devastating fungal disease that can destroy entire plants quickly in humid conditions. The same pathogen that caused the Irish Potato Famine.",
    treatment:
      "Apply preventive fungicides (mancozeb, copper, or chlorothalonil). Remove infected plants immediately, ensure good drainage and air circulation, avoid overhead watering.",
  },
  Tomato___Leaf_Mold: {
    name: "Tomato Leaf Mold",
    severity: "medium",
    description:
      "Fungal disease causing yellow spots on upper leaf surface and fuzzy olive-green growth underneath. Common in greenhouse conditions.",
    treatment:
      "Improve ventilation and reduce humidity below 85%. Apply fungicides if necessary, avoid wetting leaves when watering, and ensure adequate plant spacing.",
  },
  Tomato___Septoria_leaf_spot: {
    name: "Tomato Septoria Leaf Spot",
    severity: "medium",
    description:
      "Fungal disease causing small circular spots with dark borders and light centers on leaves. Progresses from bottom to top of plant.",
    treatment:
      "Remove affected lower leaves immediately, apply fungicide sprays, mulch around plants to prevent soil splash, and avoid overhead watering.",
  },
  "Tomato___Spider_mites_Two-spotted_spider_mite": {
    name: "Two-Spotted Spider Mites",
    severity: "medium",
    description:
      "Tiny pests causing stippling, yellowing, and fine webbing on leaves. Thrive in hot, dry conditions.",
    treatment:
      "Increase humidity around plants, use predatory mites (biological control), apply miticides if severe, and regularly spray with water to dislodge mites.",
  },
  Tomato___Target_Spot: {
    name: "Tomato Target Spot",
    severity: "medium",
    description:
      "Fungal disease causing circular spots with concentric rings on leaves and fruit. Can cause significant defoliation.",
    treatment:
      "Apply fungicides containing chlorothalonil or mancozeb. Remove infected plant debris, ensure good air circulation, and avoid overhead irrigation.",
  },
  Tomato___Tomato_Yellow_Leaf_Curl_Virus: {
    name: "Tomato Yellow Leaf Curl Virus",
    severity: "high",
    description:
      "Viral disease spread by whiteflies causing yellowing, curling, and stunting of leaves. Can severely reduce fruit production.",
    treatment:
      "Control whitefly populations with insecticides or reflective mulches. Remove infected plants immediately. Use virus-resistant varieties when possible.",
  },
  Tomato___Tomato_mosaic_virus: {
    name: "Tomato Mosaic Virus",
    severity: "high",
    description:
      "Viral disease causing mottled yellow and green patterns on leaves, stunted growth, and reduced fruit quality.",
    treatment:
      "No cure available. Remove infected plants immediately. Disinfect tools with 10% bleach solution. Plant virus-resistant varieties and control aphid vectors.",
  },
  Tomato___healthy: {
    name: "Healthy Tomato Plant",
    severity: "low",
    description:
      "Plant appears healthy with no visible signs of disease or pest damage. Continue regular monitoring and preventive care.",
    treatment:
      "Maintain good cultural practices: proper watering, adequate spacing, regular fertilization, and routine plant inspection for early disease detection.",
  },
  Potato___Early_blight: {
    name: "Potato Early Blight",
    severity: "medium",
    description:
      "Fungal disease causing dark spots with concentric rings on leaves. Can reduce tuber quality and yield.",
    treatment:
      "Apply fungicides containing chlorothalonil or mancozeb. Remove infected foliage, ensure proper plant spacing, and avoid overhead irrigation.",
  },
  Potato___Late_blight: {
    name: "Potato Late Blight",
    severity: "high",
    description:
      "Devastating fungal disease that can destroy crops rapidly in cool, wet conditions. Affects both foliage and tubers.",
    treatment:
      "Apply preventive fungicides (copper or mancozeb). Destroy infected plants immediately. Ensure good drainage and avoid overhead watering.",
  },
  Potato___healthy: {
    name: "Healthy Potato Plant",
    severity: "low",
    description:
      "Plant shows no signs of disease. Continue monitoring and maintain good agricultural practices.",
    treatment:
      "Continue regular care including proper fertilization, hill soil around stems, monitor for Colorado potato beetle, and ensure adequate moisture.",
  },
  Corn___Cercospora_leaf_spot_Gray_leaf_spot: {
    name: "Corn Gray Leaf Spot",
    severity: "medium",
    description:
      "Fungal disease causing rectangular gray lesions on leaves. Can significantly reduce yield in susceptible varieties.",
    treatment:
      "Plant resistant varieties, rotate crops, apply fungicides if severe. Remove crop debris after harvest to reduce overwintering spores.",
  },
  Corn___Common_rust: {
    name: "Corn Common Rust",
    severity: "medium",
    description:
      "Fungal disease causing small, reddish-brown pustules on leaves. Most common in cool, humid weather.",
    treatment:
      "Plant resistant hybrids, apply fungicides if conditions favor disease development. Usually not economically damaging in most conditions.",
  },
  Corn___Northern_Leaf_Blight: {
    name: "Northern Corn Leaf Blight",
    severity: "medium",
    description:
      "Fungal disease causing cigar-shaped lesions on leaves. Can cause significant yield loss in susceptible hybrids.",
    treatment:
      "Use resistant hybrids, rotate crops with non-host plants, apply fungicides if disease pressure is high. Bury crop residue after harvest.",
  },
  Corn___healthy: {
    name: "Healthy Corn Plant",
    severity: "low",
    description:
      "Plant appears healthy with normal growth and no disease symptoms visible.",
    treatment:
      "Continue standard corn production practices: adequate fertilization, weed control, and monitoring for pests and diseases.",
  },
  Apple___Apple_scab: {
    name: "Apple Scab",
    severity: "medium",
    description:
      "Fungal disease causing dark, scabby lesions on leaves and fruit. Can cause premature leaf drop and unmarketable fruit.",
    treatment:
      "Apply fungicides during wet periods in spring. Rake and destroy fallen leaves. Prune for better air circulation. Plant scab-resistant varieties.",
  },
  Apple___Black_rot: {
    name: "Apple Black Rot",
    severity: "high",
    description:
      "Fungal disease causing brown leaf spots and black, mummified fruit. Can cause significant fruit loss.",
    treatment:
      "Remove mummified fruit and infected wood. Apply fungicides during bloom and fruit development. Improve air circulation through pruning.",
  },
  Apple___Cedar_apple_rust: {
    name: "Cedar Apple Rust",
    severity: "medium",
    description:
      "Fungal disease requiring both apple and cedar hosts. Causes yellow spots on leaves and orange lesions on fruit.",
    treatment:
      "Remove nearby cedar trees if possible. Apply fungicides in spring. Plant rust-resistant apple varieties. Remove infected leaves and fruit.",
  },
  Apple___healthy: {
    name: "Healthy Apple Tree",
    severity: "low",
    description:
      "Tree shows healthy foliage and normal growth patterns with no visible disease symptoms.",
    treatment:
      "Continue routine orchard management: proper pruning, fertilization, pest monitoring, and sanitation practices.",
  },
  Grape___Black_rot: {
    name: "Grape Black Rot",
    severity: "high",
    description:
      "Fungal disease causing brown leaf spots and shriveled, black fruit. Can destroy entire grape clusters.",
    treatment:
      "Apply fungicides from bloom through fruit development. Remove mummified berries and infected canes. Ensure good air circulation.",
  },
  "Grape___Esca_(Black_Measles)": {
    name: "Grape Esca (Black Measles)",
    severity: "high",
    description:
      "Fungal trunk disease causing leaf discoloration, berry spotting, and eventual vine decline or death.",
    treatment:
      "Remove infected wood during dormant season. Apply wound protectants after pruning. Consider trunk renewal in severely affected vines.",
  },
  "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)": {
    name: "Grape Leaf Blight",
    severity: "medium",
    description:
      "Fungal disease causing brown spots on leaves that may develop yellow halos. Can cause defoliation.",
    treatment:
      "Apply fungicides during wet periods. Remove infected leaves. Ensure proper vine spacing and canopy management for air circulation.",
  },
  Grape___healthy: {
    name: "Healthy Grape Vine",
    severity: "low",
    description:
      "Vine displays healthy foliage and normal fruit development with no disease symptoms.",
    treatment:
      "Maintain good vineyard practices: proper pruning, canopy management, balanced nutrition, and regular disease monitoring.",
  },
};

// Mock AI analysis function - simulates disease detection
function simulateAIAnalysis(imageFile) {
  return new Promise((resolve) => {
    setTimeout(() => {
      const diseaseKeys = Object.keys(diseaseDatabase);
      const randomDisease =
        diseaseKeys[Math.floor(Math.random() * diseaseKeys.length)];
      const diseaseInfo = diseaseDatabase[randomDisease];

      const confidence = Math.floor(Math.random() * 23) + 75;

      resolve({
        disease: randomDisease,
        confidence: confidence,
        info: diseaseInfo,
      });
    }, 2000 + Math.random() * 1000); 
  });
}

const uploadArea = document.getElementById("uploadArea");
const fileInput = document.getElementById("fileInput");
const analyzeBtn = document.getElementById("analyzeBtn");
const previewContainer = document.getElementById("previewContainer");
const loading = document.getElementById("loading");
const resultsDiv = document.getElementById("results");

let selectedFile = null;

// File upload handling
uploadArea.addEventListener("click", () => fileInput.click());

uploadArea.addEventListener("dragover", (e) => {
  e.preventDefault();
  uploadArea.classList.add("dragover");
});

uploadArea.addEventListener("dragleave", () => {
  uploadArea.classList.remove("dragover");
});

uploadArea.addEventListener("drop", (e) => {
  e.preventDefault();
  uploadArea.classList.remove("dragover");
  uploadArea.classList.add("drag-animation");

  setTimeout(() => {
    uploadArea.classList.remove("drag-animation");
  }, 600);

  const files = e.dataTransfer.files;
  if (files.length > 0) {
    handleFileSelect(files[0]);
  }
});

fileInput.addEventListener("change", (e) => {
  if (e.target.files.length > 0) {
    handleFileSelect(e.target.files[0]);
  }
});

function handleFileSelect(file) {
  if (!file.type.startsWith("image/")) {
    alert("Please select a valid image file (JPG, PNG, WebP)");
    return;
  }

  selectedFile = file;

  const reader = new FileReader();
  reader.onload = (e) => {
    previewContainer.innerHTML = `<img src="${e.target.result}" alt="Plant preview" class="preview-image">`;
    analyzeBtn.disabled = false;
    resultsDiv.innerHTML = "";
  };
  reader.readAsDataURL(file);
}

// Analysis function
analyzeBtn.addEventListener("click", async () => {
  if (!selectedFile) return;

  loading.style.display = "block";
  resultsDiv.innerHTML = "";
  analyzeBtn.disabled = true;

  try {
    const result = await simulateAIAnalysis(selectedFile);

    loading.style.display = "none";

    displayResults(result);
  } catch (error) {
    console.error("Analysis error:", error);
    loading.style.display = "none";
    resultsDiv.innerHTML = `
                    <div class="result-card" style="border-left-color: #dc3545;">
                        <div class="disease-name" style="color: #dc3545;">❌ Analysis Failed</div>
                        <div class="description">Unable to analyze the image. Please try again with a clearer image.</div>
                    </div>
                `;
  }

  analyzeBtn.disabled = false;
});

function displayResults(result) {
  const { disease, confidence, info } = result;

  const severityClass = info.severity;
  const severityEmoji = {
    low: "✅",
    medium: "⚠️",
    high: "🚨",
  };

  resultsDiv.innerHTML = `
                <div class="result-card">
                    <div class="disease-name">${severityEmoji[severityClass]} ${
    info.name
  }</div>
                    <div class="confidence">Confidence: ${confidence}%</div>
                    <div class="severity ${severityClass}">
                        Severity: ${
                          info.severity.charAt(0).toUpperCase() +
                          info.severity.slice(1)
                        }
                    </div>
                    <div class="description">${info.description}</div>
                    <div class="treatment">
                        <h4>🌿 Treatment Recommendations</h4>
                        <p>${info.treatment}</p>
                    </div>
                </div>
            `;
}

// Modal functionality
function openModal(modalId) {
  document.getElementById(modalId).style.display = "block";
  document.body.style.overflow = "hidden";
}

function closeModal(modalId) {
  document.getElementById(modalId).style.display = "none";
  document.body.style.overflow = "auto";
}

// Add event listeners for modal close buttons
document.querySelectorAll(".close").forEach((closeBtn) => {
  closeBtn.addEventListener("click", (e) => {
    const modal = e.target.closest(".modal");
    modal.style.display = "none";
    document.body.style.overflow = "auto";
  });
});

// Close modal when clicking outside
document.querySelectorAll(".modal").forEach((modal) => {
  modal.addEventListener("click", (e) => {
    if (e.target === modal) {
      modal.style.display = "none";
      document.body.style.overflow = "auto";
    }
  });
});

// Keyboard navigation for modals
document.addEventListener("keydown", (e) => {
  if (e.key === "Escape") {
    document.querySelectorAll(".modal").forEach((modal) => {
      if (modal.style.display === "block") {
        modal.style.display = "none";
        document.body.style.overflow = "auto";
      }
    });
  }
});

// Initialize page
document.addEventListener("DOMContentLoaded", () => {
  console.log("🌱 Plant Disease Detection System Initialized");
  console.log(
    "📊 Disease Database loaded with",
    Object.keys(diseaseDatabase).length,
    "diseases"
  );

  document.querySelector(".header").style.opacity = "0";
  document.querySelector(".header").style.transform = "translateY(-20px)";

  setTimeout(() => {
    document.querySelector(".header").style.transition = "all 0.6s ease";
    document.querySelector(".header").style.opacity = "1";
    document.querySelector(".header").style.transform = "translateY(0)";
  }, 100);
});

// Additional utility functions
function validateImage(file) {
  const validTypes = ["image/jpeg", "image/jpg", "image/png", "image/webp"];
  const maxSize = 10 * 1024 * 1024; 

  if (!validTypes.includes(file.type)) {
    throw new Error(
      "Invalid file type. Please upload JPG, PNG, or WebP images only."
    );
  }

  if (file.size > maxSize) {
    throw new Error("File too large. Please upload images smaller than 10MB.");
  }

  return true;
}

// Enhanced file handling with validation
function handleFileSelect(file) {
  try {
    validateImage(file);
    selectedFile = file;

    previewContainer.innerHTML = '<div class="spinner"></div>';

    const reader = new FileReader();
    reader.onload = (e) => {
      previewContainer.innerHTML = `<img src="${e.target.result}" alt="Plant preview" class="preview-image">`;
      analyzeBtn.disabled = false;
      resultsDiv.innerHTML = "";

      document.getElementById("modelStatus").innerHTML =
        "🔍 Image loaded - Ready for analysis";
      document.getElementById("modelStatus").className =
        "status-indicator status-warning";
    };

    reader.onerror = () => {
      previewContainer.innerHTML =
        '<div class="no-results">❌ Error loading image</div>';
      selectedFile = null;
    };

    reader.readAsDataURL(file);
  } catch (error) {
    alert(error.message);
    previewContainer.innerHTML =
      '<div class="no-results">📷 Upload an image to get started</div>';
    selectedFile = null;
    analyzeBtn.disabled = true;
  }
}

// Add some sample data for demonstration
const sampleAnalysisResults = [
  { disease: "Tomato___Early_blight", confidence: 89 },
  { disease: "Potato___Late_blight", confidence: 94 },
  { disease: "Apple___Apple_scab", confidence: 87 },
  { disease: "Grape___Black_rot", confidence: 92 },
  { disease: "Corn___Northern_Leaf_Blight", confidence: 85 },
  { disease: "Tomato___healthy", confidence: 96 },
];

// Enhanced simulation function
function simulateAIAnalysis(imageFile) {
  return new Promise((resolve) => {
    const randomResult =
      sampleAnalysisResults[
        Math.floor(Math.random() * sampleAnalysisResults.length)
      ];
    const diseaseInfo = diseaseDatabase[randomResult.disease];

    setTimeout(() => {
      resolve({
        disease: randomResult.disease,
        confidence: randomResult.confidence + Math.floor(Math.random() * 6) - 3, 
        info: diseaseInfo,
      });
    }, 1500 + Math.random() * 1500);
  });
}
