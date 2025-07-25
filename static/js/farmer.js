// Utility: Create a list item with a delete button
function createListItem(text) {
  const li = document.createElement('li');
  li.textContent = text;

  const deleteBtn = document.createElement('button');
  deleteBtn.textContent = 'Delete';
  deleteBtn.classList.add('delete-btn');
  deleteBtn.addEventListener('click', () => {
    li.remove();
  });

  li.appendChild(deleteBtn);
  return li;
}

// Sell Product Form
const productForm = document.getElementById('product-form');
const productDisplay = document.getElementById('product-display');

productForm.addEventListener('submit', function (e) {
  e.preventDefault();

  const sellerName = document.getElementById('seller-name').value.trim();
  const contact = document.getElementById('seller-contact').value.trim();
  const name = document.getElementById('product-name').value.trim();
  const quantity = document.getElementById('product-quantity').value.trim();
  const price = document.getElementById('product-price').value.trim();

  if (sellerName && contact && name && quantity && price) {
    const text = `${name} - ${quantity} units - ₹${price} (Seller: ${sellerName}, Contact: ${contact})`;
    const li = createListItem(text);
    productDisplay.appendChild(li);

    productForm.reset();
  }
});

// Buy Product Form
const buyForm = document.getElementById('buy-form');
const buyRequestDisplay = document.getElementById('buy-request-display');

buyForm.addEventListener('submit', function (e) {
  e.preventDefault();

  const buyerName = document.getElementById('buyer-name').value.trim();
  const buyerContact = document.getElementById('buyer-contact').value.trim();
  const productToBuy = document.getElementById('buy-product-name').value.trim();
  const buyQuantity = document.getElementById('buy-product-quantity').value.trim();

  if (buyerName && buyerContact && productToBuy && buyQuantity) {
    const text = `Request by ${buyerName} for ${buyQuantity} units of "${productToBuy}" (Contact: ${buyerContact})`;
    const li = createListItem(text);
    buyRequestDisplay.appendChild(li);

    buyForm.reset();
  }
});

<button onclick="window.location.href='main.html'">Back to Main</button>
