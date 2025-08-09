const formContainer = document.getElementById('formContainer');

document.querySelectorAll('.loan-card').forEach(card => {
    card.addEventListener('click', () => {
        const loanType = card.dataset.type;
        loadForm(loanType);
    });
});

function loadForm(type) {
    let formHTML = '';

    if (type === 'crop') {
        formHTML = `
      <form id="loanForm" class="loan-form">
        <h2>Crop Cultivation Loan Details</h2>
        ${commonFields()}
        <label>Crop Type<span class="required-star">*</span>: <input type="text" name="cropType" required></label>
        <label>Expected Yield (Quintals)<span class="required-star">*</span>: <input type="number" name="expectedYield" required></label>
        <label>Irrigation Type<span class="required-star">*</span>:
          <select name="irrigation" required>
            <option value="Assured">Assured</option>
            <option value="Rain-fed">Rain-fed</option>
          </select>
        </label>
        <label>Enrolled in PMFBY<span class="required-star">*</span>:
          <select name="pmfby" required>
            <option value="Yes">Yes</option>
            <option value="No">No</option>
          </select>
        </label>
        <button type="submit">Check Eligibility</button>
      </form>
    `;
    } else if (type === 'equipment') {
        formHTML = `
      <form id="loanForm" class="loan-form">
        <h2>Farm Equipment Loan Details</h2>
        ${commonFields()}
        <label>Equipment Type<span class="required-star">*</span>: <input type="text" name="equipmentType" required></label>
        <label>Equipment Cost (₹)<span class="required-star">*</span>: <input type="number" name="equipmentCost" required></label>
        <label>Expected Increase in Productivity (%)<span class="required-star">*</span>: <input type="number" name="productivityIncrease" required></label>
        <label>Collateral Offered<span class="required-star">*</span>: <input type="text" name="collateral" required></label>
        <button type="submit">Check Eligibility</button>
      </form>
    `;
    } else if (type === 'water') {
        formHTML = `
      <form id="loanForm" class="loan-form">
        <h2>Water Source Development Loan Details</h2>
        ${commonFields()}
        <label>Water Source Purpose<span class="required-star">*</span>: <input type="text" name="waterPurpose" required></label>
        <label>Soil Suitability Certificate Available<span class="required-star">*</span>:
          <select name="soilCertificate" required>
            <option value="Yes">Yes</option>
            <option value="No">No</option>
          </select>
        </label>
        <label>Water Availability Certificate<span class="required-star">*</span>:
          <select name="waterCertificate" required>
            <option value="Yes">Yes</option>
            <option value="No">No</option>
          </select>
        </label>
        <label>Collateral Offered<span class="required-star">*</span>: <input type="text" name="collateral" required></label>
        <button type="submit">Check Eligibility</button>
      </form>
    `;
    } else if (type === 'land') {
        formHTML = `
      <form id="loanForm" class="loan-form">
        <h2>Land Purchase Loan Details</h2>
        ${commonFields()}
        <label>Land Location<span class="required-star">*</span>: <input type="text" name="landLocation" required></label>
        <label>Land Area to Purchase (Acres)<span class="required-star">*</span>: <input type="number" name="landAreaPurchase" required></label>
        <label>Land Cost (₹)<span class="required-star">*</span>: <input type="number" name="landCost" required></label>
        <label>Soil Quality<span class="required-star">*</span>: <input type="text" name="soilQuality" required></label>
        <label>Encumbrance Certificate Available<span class="required-star">*</span>:
          <select name="encumbranceCertificate" required>
            <option value="Yes">Yes</option>
            <option value="No">No</option>
          </select>
        </label>
        <label>Loan-to-Value Ratio (%)<span class="required-star">*</span>: <input type="number" name="ltvRatio" required></label>
        <button type="submit">Check Eligibility</button>
      </form>
    `;
    }

    formContainer.innerHTML = formHTML;

    if (document.getElementById('loanForm')) {
        document.getElementById('loanForm').addEventListener('submit', handleFormSubmit);
    }
}

function commonFields() {
    return `
    <label>Farmer Name<span class="required-star">*</span>: <input type="text" name="farmerName" required></label>
    <label>State<span class="required-star">*</span>: <input type="text" name="state" required></label>
    <label>District<span class="required-star">*</span>: <input type="text" name="district" required></label>
    <label>Land Ownership<span class="required-star">*</span>:
      <select name="landOwnership" required>
        <option value="Owned">Owned</option>
        <option value="Leased">Leased</option>
        <option value="Jointly Owned">Jointly Owned</option>
      </select>
    </label>
    <label>Land Area (in Acres)<span class="required-star">*</span>: <input type="number" name="landArea" required></label>
    <label>Land Records Available<span class="required-star">*</span>:
      <select name="landRecords" required>
        <option value="Yes">Yes</option>
        <option value="No">No</option>
      </select>
    </label>
    <label>CIBIL Score<span class="required-star">*</span>: <input type="number" name="cibilScore" required></label>
    <label>Past Loan Repayment<span class="required-star">*</span>:
      <select name="loanHistory" required>
        <option value="Good">Good</option>
        <option value="Delayed">Delayed</option>
        <option value="Defaulted">Defaulted</option>
        <option value="No Previous Loan">No Previous Loan</option>
      </select>
    </label>
  `;
}

function handleFormSubmit(e) {
    e.preventDefault();

    const formData = new FormData(e.target);
    const data = {};
    formData.forEach((value, key) => {
        data[key] = value;
    });

    document.getElementById('statusMessage').innerText = 'Analyzing...';

    function renderMarkdown(text) {
        // Convert Headings
        text = text.replace(/^### (.*$)/gim, '<h3>$1</h3>');
        text = text.replace(/^## (.*$)/gim, '<h2>$1</h2>');
        text = text.replace(/^# (.*$)/gim, '<h1>$1</h1>');

        // Convert Bold (**bold**)
        text = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');

        // Convert bullet points
        text = text.replace(/^- (.*$)/gim, '<li>$1</li>');

        // Wrap list items with <ul>
        text = text.replace(/(<li>.*<\/li>)/gs, '<ul>$1</ul>');

        // Line breaks
        text = text.replace(/\n/g, '<br>');

        return text.trim();
    }

    document.getElementById('printButton').addEventListener('click', function () {
        const contentToPrint = document.getElementById('geminiResponseContainer').innerHTML;

        const printWindow = window.open('', '', 'height=600,width=800');
        printWindow.document.write('<html><head><title>Loan Eligibility Report</title>');
        printWindow.document.write('<style>body { font-family: Poppins, sans-serif; padding: 20px; } h1, h2, h3 { color: #333; } ul { padding-left: 20px; } </style>');
        printWindow.document.write('</head><body>');
        printWindow.document.write('<h1>Loan Eligibility Report</h1>');
        printWindow.document.write(contentToPrint);
        printWindow.document.write('</body></html>');
        printWindow.document.close();
        printWindow.print();
    });

        // Send JSON to Python backend (Flask/FastAPI API endpoint)
    fetch('http://localhost:5000/process-loan', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
        .then(response => response.json())
        .then(result => {
            document.getElementById('statusMessage').innerText = 'Analysis Complete!';
            const formattedHTML = renderMarkdown(result.message);
            document.getElementById('geminiResponseContainer').innerHTML = formattedHTML;
            document.getElementById('printButton').style.display = 'inline-block';
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Failed to send data to backend');
        });
}