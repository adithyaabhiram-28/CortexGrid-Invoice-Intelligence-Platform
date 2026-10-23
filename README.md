# CortexGrid: Invoice Intelligence Platform

CortexGrid is a web-based invoice processing and verification platform. It extracts invoice information from PDF documents and helps reviewers identify potential discrepancies against registered vendor and purchase-order records.

## Current Features

- User login and dashboard.
- Uploading invoice PDF documents.
- Extracting embedded text from digital PDFs and using OCR for scanned PDFs.
- Displaying extracted invoice information and recognized text.
- Vendor management and vendor matching.
- Creating and managing purchase orders and their line items.
- Associating invoices with purchase orders and comparing totals.
- Detecting duplicate invoices, unregistered vendors, missing purchase orders, and amount discrepancies.
- Explainable, rule-based invoice risk scoring.
- Invoice search, status views, and risk filters.

## Technology Stack

- **Frontend:** React
- **Backend:** Python and Flask
- **Database:** PostgreSQL
- **Database access:** SQLAlchemy / relational database access
- **OCR:** Tesseract OCR for scanned PDFs
- **Testing:** Pytest for backend tests and frontend production build validation

## Important Scope Note

The current risk score is based on predefined verification rules. CortexGrid does **not** currently include a verified, trained machine-learning fraud classifier. Optional Gemini-based summarization requires API configuration and is not part of the verified core workflow.

## Project Structure

The repository is expected to contain the existing project folders, typically:

```text
CortexGrid/
├── backend/
├── frontend/
├── .gitignore
└── README.md
```

Preserve the actual folder structure in your local checkout if it differs from this example.

## Running Locally

Use the project's existing setup instructions and dependency files. Configure local environment variables in a `.env` file that is **not committed** to Git. Use `.env.example` to document required variable names without including real passwords, tokens, or API keys.

Typical development workflow:

1. Configure the backend environment and database connection.
2. Start the Flask backend using the project's existing run command.
3. Install frontend dependencies from the frontend package manifest.
4. Start the React development server.

Do not commit real invoice documents, production data, database backups, credentials, or private configuration files.

## Testing Status

At the last recorded validation:

- Backend automated tests: **20 passed**.
- Frontend production build: **successful**.
- Manual checks covered PDF extraction, scanned-PDF OCR, vendor/PO verification, duplicate detection, amount variance, invalid-file handling, and data persistence.
