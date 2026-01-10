let products = [];
let requests = [];

// DOM elements
const tabButtons = document.querySelectorAll(".tab-button");
const sections = document.querySelectorAll(".section");
const productForm = document.getElementById("product-form");
const buyForm = document.getElementById("buy-form");
const productDisplay = document.getElementById("product-display");
const buyRequestDisplay = document.getElementById("buy-request-display");
const productCount = document.getElementById("product-count");
const requestCount = document.getElementById("request-count");

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

// Initialize
renderProducts();
renderRequests();
