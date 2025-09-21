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

  const formData = new FormData(productForm);
  const product = {
    sellerName: document.getElementById("seller-name").value.trim(),
    contact: document.getElementById("seller-contact").value.trim(),
    name: document.getElementById("product-name").value.trim(),
    quantity: document.getElementById("product-quantity").value.trim(),
    price: document.getElementById("product-price").value.trim(),
  };

  if (Object.values(product).every((value) => value)) {
    products.push(product);
    renderProducts();
    productForm.reset();
    showSuccessMessage(productDisplay, "Product added successfully!");
  }
});

buyForm.addEventListener("submit", function (e) {
  e.preventDefault();

  const request = {
    buyerName: document.getElementById("buyer-name").value.trim(),
    contact: document.getElementById("buyer-contact").value.trim(),
    productName: document.getElementById("buy-product-name").value.trim(),
    quantity: document.getElementById("buy-product-quantity").value.trim(),
  };

  if (Object.values(request).every((value) => value)) {
    requests.push(request);
    renderRequests();
    buyForm.reset();
    showSuccessMessage(
      buyRequestDisplay,
      "Buy request submitted successfully!"
    );
  }
});

// Initialize
renderProducts();
renderRequests();
