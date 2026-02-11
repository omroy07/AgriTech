# Security Policy

AgriTech is committed to ensuring the safety of agricultural data and the integrity of our Flask-based ecosystem. We value the input of security researchers and the open-source community.

> [!IMPORTANT]
> **Do NOT open a public GitHub issue for security vulnerabilities.** Please follow the private reporting process below.

## Safe Harbor
Any researcher who follows this policy while reporting a vulnerability will be considered to be in compliance with this policy. We will not initiate legal action against you for research conducted within these boundaries.

## How to Report
Please report security vulnerabilities privately to the maintainers. 

### Vulnerability Report Template
To help us triage your report quickly, please include:
1. **Title**: Concise summary of the issue.
2. **Impact**: How could this be exploited? (e.g., Data breach, Remote Code Execution).
3. **Affected App**: (e.g., Disease Prediction, Crop Yield App).
4. **Steps to Reproduce**: Minimal steps or a PoC script.
5. **Recommended Fix**: If you have a suggestion for remediation.

## Scope
This policy applies to all sub-applications within the AgriTech repository, including but not limited to:
* Disease Prediction (File Uploads)
* Crop Recommendation (Input Validation)
* Forum (XSS/Auth)
* All internal Database Migrations

## 🛠 Security Implementation Reference
For detailed documentation on how we have mitigated SQLi, XSS, and File Upload vulnerabilities, please refer to our **[Security Implementation Guide](docs/SECURITY_IMPLEMENTATION.md)**.

---
*AgriTech - Securing the future of farming.*
