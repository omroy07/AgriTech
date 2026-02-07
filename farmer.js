let products = [];
let requests = [];
let predictions = [];

// DOM elements
const tabButtons = document.querySelectorAll(".tab-button");
const sections = document.querySelectorAll(".section");
const productForm = document.getElementById("product-form");
const buyForm = document.getElementById("buy-form");
const productDisplay = document.getElementById("product-display");
const buyRequestDisplay = document.getElementById("buy-request-display");
const predictionHistoryDisplay = document.getElementById("prediction-history-display");
const productCount = document.getElementById("product-count");
const requestCount = document.getElementById("request-count");
const historyCount = document.getElementById("history-count");

// Validation functions
function validateContactNumber(phone) {
  const phoneRegex = /^[0-9]{10}$/;
  return phoneRegex.test(phone.replace(/[\s\-()]/g, ''));
}

function validateQuantity(quantity) {
  const quantityNum = parseFloat(quantity);
  return !isNaN(quantityNum) && quantityNum > 0;
}

function showErrorMessage(container, message) {
  const existingError = container.querySelector(".error-message");
  if (existingError) {
    existingError.remove();
  }

  const errorDiv = document.createElement("div");
  errorDiv.className = "error-message";
  errorDiv.innerHTML = `
    <i class="fas fa-exclamation-circle"></i>
    <span>${message}</span>
  `;

  container.insertBefore(errorDiv, container.firstChild);

  setTimeout(() => {
    errorDiv.remove();
  }, 4000);
}

// Tab switching functionality
tabButtons.forEach((button) => {
  button.addEventListener("click", () => {
    const sectionId = button.dataset.section;

    tabButtons.forEach((btn) => btn.classList.remove("active"));
    button.classList.add("active");

    sections.forEach((section) => section.classList.remove("active"));
    document.getElementById(`${sectionId}-section`).classList.add("active");
  });
});

// Utility functions
function showSuccessMessage(container, message) {
  const existingMessage = container.querySelector(".success-message");
  if (existingMessage) {
    existingMessage.remove();
  }

  const successDiv = document.createElement("div");
  successDiv.className = "success-message";
  successDiv.innerHTML = `
                <i class="fas fa-check-circle"></i>
                <span>${message}</span>
            `;

  container.insertBefore(successDiv, container.firstChild);

  setTimeout(() => {
    successDiv.remove();
  }, 3000);
}

function updateProductCount() {
  productCount.textContent = `${products.length} Product${
    products.length !== 1 ? "s" : ""
  }`;
}

function updateRequestCount() {
  requestCount.textContent = `${requests.length} Request${
    requests.length !== 1 ? "s" : ""
  }`;
}

function updateHistoryCount() {
  historyCount.textContent = `${predictions.length} Prediction${
    predictions.length !== 1 ? "s" : ""
  }`;
}

function createProductItem(product, index) {
  return `
                <div class="listing-item">
                    <div class="listing-header">
                        <div>
                            <div class="listing-title">${product.name}</div>
                            <div class="listing-price">${product.price}</div>
                        </div>
                        <button class="delete-btn" onclick="removeProduct(${index})">
                            <i class="fas fa-trash"></i> Delete
                        </button>
                    </div>
                    <div class="listing-details">
                        <div class="listing-detail">
                            <i class="fas fa-user"></i>
                            <span>Seller: ${product.sellerName}</span>
                        </div>
                        <div class="listing-detail">
                            <i class="fas fa-phone"></i>
                            <span>${product.contact}</span>
                        </div>
                        <div class="listing-detail">
                            <i class="fas fa-weight"></i>
                            <span>Quantity: ${product.quantity}</span>
                        </div>
                        <div class="listing-detail">
                            <i class="fas fa-clock"></i>
                            <span>Listed: ${new Date().toLocaleDateString()}</span>
                        </div>
                    </div>
                </div>
            `;
}

function createRequestItem(request, index) {
  return `
                <div class="listing-item">
                    <div class="listing-header">
                        <div>
                            <div class="listing-title">Looking for: ${
                              request.productName
                            }</div>
                        </div>
                        <button class="delete-btn" onclick="removeRequest(${index})">
                            <i class="fas fa-trash"></i> Delete
                        </button>
                    </div>
                    <div class="listing-details">
                        <div class="listing-detail">
                            <i class="fas fa-user"></i>
                            <span>Buyer: ${request.buyerName}</span>
                        </div>
                        <div class="listing-detail">
                            <i class="fas fa-phone"></i>
                            <span>${request.contact}</span>
                        </div>
                        <div class="listing-detail">
                            <i class="fas fa-weight"></i>
                            <span>Needed: ${request.quantity}</span>
                        </div>
                        <div class="listing-detail">
                            <i class="fas fa-clock"></i>
                            <span>Requested: ${new Date().toLocaleDateString()}</span>
                        </div>
                    </div>
                </div>
            `;
}

function renderProducts() {
  if (products.length === 0) {
    productDisplay.innerHTML = `
                    <div class="empty-state">
                        <i class="fas fa-box-open"></i>
                        <p>No products listed yet. Add your first product!</p>
                    </div>
                `;
  } else {
    productDisplay.innerHTML = products
      .map((product, index) => createProductItem(product, index))
      .join("");
  }
  updateProductCount();
}

function renderRequests() {
  if (requests.length === 0) {
    buyRequestDisplay.innerHTML = `
                    <div class="empty-state">
                        <i class="fas fa-clipboard-list"></i>
                        <p>No buy requests yet. Submit your first request!</p>
                    </div>
                `;
  } else {
    buyRequestDisplay.innerHTML = requests
      .map((request, index) => createRequestItem(request, index))
      .join("");
  }
  updateRequestCount();
}

// Global functions for delete buttons
window.removeProduct = function (index) {
  products.splice(index, 1);
  renderProducts();
  showSuccessMessage(productDisplay, "Product removed successfully!");
};

window.removeRequest = function (index) {
  requests.splice(index, 1);
  renderRequests();
  showSuccessMessage(buyRequestDisplay, "Request removed successfully!");
};

// Form submissions
productForm.addEventListener("submit", function (e) {
  e.preventDefault();

  const sellerName = document.getElementById("seller-name").value.trim();
  const sellerContact = document.getElementById("seller-contact").value.trim();
  const productName = document.getElementById("product-name").value.trim();
  const productQuantity = document.getElementById("product-quantity").value.trim();
  const productPrice = document.getElementById("product-price").value.trim();

  // Validate contact number
  if (!validateContactNumber(sellerContact)) {
    showErrorMessage(productForm, "❌ Contact number must be a valid 10-digit mobile number (e.g., 9876543210)");
    return;
  }

  // Validate quantity
  if (!validateQuantity(productQuantity)) {
    showErrorMessage(productForm, "❌ Quantity must be a positive number (e.g., 500 kg)");
    return;
  }

  // Check all fields are filled
  if (!sellerName || !productName || !productPrice) {
    showErrorMessage(productForm, "❌ Please fill in all required fields");
    return;
  }

  const product = {
    sellerName: sellerName,
    contact: sellerContact,
    name: productName,
    quantity: productQuantity,
    price: productPrice,
  };

  products.push(product);
  renderProducts();
  productForm.reset();
  showSuccessMessage(productDisplay, "✅ Product added successfully!");
});

buyForm.addEventListener("submit", function (e) {
  e.preventDefault();

  const buyerName = document.getElementById("buyer-name").value.trim();
  const buyerContact = document.getElementById("buyer-contact").value.trim();
  const productName = document.getElementById("buy-product-name").value.trim();
  const quantity = document.getElementById("buy-product-quantity").value.trim();

  // Validate contact number
  if (!validateContactNumber(buyerContact)) {
    showErrorMessage(buyForm, "❌ Contact number must be a valid 10-digit mobile number (e.g., 9876543210)");
    return;
  }

  // Validate quantity
  if (!validateQuantity(quantity)) {
    showErrorMessage(buyForm, "❌ Quantity must be a positive number (e.g., 1000 kg)");
    return;
  }

  // Check all fields are filled
  if (!buyerName || !productName) {
    showErrorMessage(buyForm, "❌ Please fill in all required fields");
    return;
  }

  const request = {
    buyerName: buyerName,
    contact: buyerContact,
    productName: productName,
    quantity: quantity,
  };

  requests.push(request);
  renderRequests();
  buyForm.reset();
  showSuccessMessage(
    buyRequestDisplay,
    "✅ Buy request submitted successfully!"
  );
});

function renderPredictions() {
  if (predictions.length === 0) {
    predictionHistoryDisplay.innerHTML = `
                    <div class="empty-state">
                        <i class="fas fa-chart-line"></i>
                        <h3>No prediction history yet 📊</h3>
                        <p>Use our AI tools to get crop recommendations and yield predictions. Your history will appear here.</p>
                    </div>
                `;
  } else {
    predictionHistoryDisplay.innerHTML = predictions
      .map((prediction, index) => createPredictionItem(prediction, index))
      .join("");
  }
  updateHistoryCount();
}

function createPredictionItem(prediction, index) {
  return `
                <div class="listing-item">
                    <div class="listing-header">
                        <div>
                            <div class="listing-title">${prediction.crop}</div>
                            <div class="listing-price">Predicted Yield: ${prediction.yield}</div>
                        </div>
                        <button class="delete-btn" onclick="removePrediction(${index})">
                            <i class="fas fa-trash"></i> Delete
                        </button>
                    </div>
                    <div class="listing-details">
                        <div class="listing-detail">
                            <i class="fas fa-seedling"></i>
                            <span>Crop: ${prediction.crop}</span>
                        </div>
                        <div class="listing-detail">
                            <i class="fas fa-clock"></i>
                            <span>Predicted: ${new Date(prediction.date).toLocaleDateString()}</span>
                        </div>
                    </div>
                </div>
            `;
}

// Global function for delete prediction
window.removePrediction = function (index) {
  predictions.splice(index, 1);
  renderPredictions();
  showSuccessMessage(predictionHistoryDisplay, "Prediction removed successfully!");
};

// Initialize
renderProducts();
renderRequests();
renderPredictions();
            // --- Cursor Trailing Effect ---
const container = document.getElementById('cursorTrail');
const circleCount = 12;
const circles = [];

let mouseX = 0;
let mouseY = 0;

// Create circles
for (let i = 0; i < circleCount; i++) {
    const circle = document.createElement('div');
    circle.classList.add('cursor-circle');
    container.appendChild(circle);
    circles.push({ el: circle, x: 0, y: 0 });
}

// Mouse move
document.addEventListener('mousemove', (e) => {
    mouseX = e.clientX;
    mouseY = e.clientY;
});

// Click effects
document.addEventListener('mousedown', () => {
    circles.forEach(c => c.el.classList.add('cursor-clicking'));
});
document.addEventListener('mouseup', () => {
    circles.forEach(c => c.el.classList.remove('cursor-clicking'));
});

// Hover effects on interactive elements
document.addEventListener('mouseover', (e) => {
    if (e.target.closest('a, button, .cta-button, .service-card, .shipment-card')) {
        circles.forEach(c => c.el.classList.add('cursor-hovering'));
    }
});
document.addEventListener('mouseout', (e) => {
    if (e.target.closest('a, button, .cta-button, .service-card, .shipment-card')) {
        circles.forEach(c => c.el.classList.remove('cursor-hovering'));
    }
});

// Animate trailing effect
function animateCursor() {
    let x = mouseX;
    let y = mouseY;

    circles.forEach((circle) => {
        circle.x += (x - circle.x) * 0.25;
        circle.y += (y - circle.y) * 0.25;

        circle.el.style.left = circle.x + 'px';
        circle.el.style.top = circle.y + 'px';

        x = circle.x;
        y = circle.y;
    });

    requestAnimationFrame(animateCursor);
}
animateCursor();