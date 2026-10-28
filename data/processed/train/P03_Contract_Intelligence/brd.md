# Business Requirement Specification – Contract Intelligence
| Field | Value |
|---|---|
| Version | 1.2 |
| Date | 12 Mar 2025 |
| Business Owner | Legal Operations |
| Status | Draft |

# Summary
Contract Intelligence (CI) will let the Legal team upload signed customer contracts, extract metadata, terms and clauses, and score seven commercial levers (P3 Levers) as Red, Amber or Green (RAG) against company standards.
MVP1 covers contract upload, processing, extraction, RAG scoring and the Contract Overview page. MVP2 adds ad-hoc analysis of draft contracts, renewal alerts and integration with the CRM account hierarchy.

# Background
Customer contracts across the CSS, UBS and ESS SBUs are stored as PDF or Word files on shared drives and reviewed manually.
Reviews are slow and inconsistent, and commercial risk across a customer's contracts is not visible.

# Goals & Objectives
Extract contract metadata and clauses automatically. Score P3 Levers consistently against company standards. Give Legal and account teams one view of commercial risk per customer. Reduce contract review time by 60%.
Open question: confirm with business owner.

# Project Scope
- In scope (MVP1): Contract upload with mandatory attributes, blob storage, processing and OCR, metadata and clause extraction, RAG scoring of seven P3 Levers, Contract Overview page and contract details page
- In scope (MVP2): Ad-hoc analysis of draft contracts, renewal and expiry alerts, CRM account hierarchy integration, bulk upload
- Out of scope: Editing extracted clauses, manual override of RAG scores, e-signature, contract authoring

# Appendix: MVP1 Overview

## Contract Intelligence MVP1 Scope Overview
- Contract Upload: Upload one signed contract with attributes.
- Processing and Extraction: OCR, metadata and clause extraction.
- RAG Scoring – Seven P3 Levers scored against standards.
- Contract Overview: Search, filters, summary and lever status.

## How it works
- Legal uploads a contract with attributes.
- The file is stored and processed.
- Metadata and clauses are extracted.
- Levers are scored.
- Results appear on Contract Overview.

### Data sources for MVP
- Signed contracts
- Standard Clause Library
- SBU/customer mapping

### Security
- Azure AD SSO
- Persona-based access
- Customer persona limited to assigned customers

## Exclusions
- No draft contract analysis
- No renewal alerts
- No CRM integration
- No bulk upload
Note: to be validated with the backend architects.

# User Roles
| Persona | Responsibilities |
|---|---|
| Legal | Upload contracts, view all contracts and analysis |
| Admin | All Legal access plus user management, SBU/customer mapping and the Standard Clause Library |
| Customer (account manager) | Read-only access to Contract Overview and Contracts for assigned customers only; no Upload menu |

# Sample Use Cases & User Stories
- As Legal, I can upload a signed contract with SBU, customer and contract type and see it processed within 15 minutes.
- As an account manager, I can see Summary ('3 Critical, 2 Medium terms') and P3 Lever Status counts for my customers.
- As Legal, I can open a contract and see each P3 Lever with clause text, page reference and RAG reason.
- As Admin, I can change a lever threshold and existing contracts are re-scored with history retained.

# NFRs
| Area | Requirement |
|---|---|
| Availability | 99.5% during 06:00–22:00 local time. |
| Security | Azure AD SSO; persona-based menus; direct-URL access to restricted pages denied. Encryption at rest and in transit. |
| Performance | Processing of a 50-page contract within 15 minutes. Contract Overview loads within 3 seconds for 5,000 contracts. |
| Observability | Processing logs in Datadog with contract reference; failure email to uploader. |
| Compliance | Audit log of upload, view and archive actions. |

# Functional Requirements

## MVP1
- Upload of one PDF or DOCX contract (max 25 MB, not password protected) with SBU, customer, contract type, name, effective and expiration date.
- Storage of the original in Azure Blob Storage and processing with OCR for scanned documents; statuses Uploaded, Processing, Completed, Failed.
- Extraction of metadata (parties, dates, renewal type, governing law, notice period) and clauses with page references.
- RAG scoring of seven P3 Levers: Payment Terms (Green ≤45 days, Amber 46–60, Red >60 or missing), Freight, Cost of Service MOQ/MOS, Restocking Fees, Customer Rebates, Cost Pass Through, Contract Price Obligations.
- Contract Overview with search (customer, account number, contract name, min 3 characters), Active/Expired view, Expiring-in filter (30/60/90/180 days), Summary and P3 Lever Status, expand/collapse per customer.

## MVP2
- Ad-hoc analysis of unsigned drafts against the Standard Clause Library.
- Renewal and expiry email alerts.
- CRM account hierarchy integration.
- Bulk upload.

## Admin
- Standard Clause Library and threshold maintenance; RAG recalculation on change with previous result kept in history.
Open question: confirm with business owner.

# Integrations

## Identity & Access
- Azure AD groups mapped to Legal, Admin and Customer personas.

## AI Services
- Azure Document Intelligence for OCR and layout; Azure OpenAI for clause extraction and scoring rationale.

## Data & Storage
- Azure Blob Storage for files; Azure PostgreSQL for metadata, clauses and scores.

## Orchestration
- Azure Service Bus between upload and processing; Azure Function for failure notifications via SendGrid.
Open question: confirm with business owner.

# Technical Overview
Refer to architecture diagram P03_Contract_Intelligence_Architecture.png.

# Data Sources
Data includes customer contracts, extracted metadata and clauses, RAG scores and the Standard Clause Library.
| Data | Description | Source | Frequency | Owner | Security |
|---|---|---|---|---|---|
| Customer contracts | Signed PDF/DOCX | Legal upload | Ad-hoc | Legal | Restricted |
| Extracted metadata and clauses | Parties, dates, clauses | Tool output | Per contract | Legal | Restricted |
| RAG scores | Lever colour and reason | Tool output | Per contract | Legal | Restricted |
| Standard Clause Library | Thresholds and standard clauses | Admin configuration | As needed | Admin | Internal |
| SBU/customer mapping | Customer to SBU | Admin configuration | As needed | Admin | Internal |
- Quality checks: Mandatory metadata present, clause-to-page references valid, all seven levers scored or marked 'Clause not found'
- RBAC: Customer persona restricted to assigned customers; all access audited

# Security, Privacy & Compliance
- AI Governance Council approval
- Contracts are restricted data; masked contracts for testing

# Constraints and Assumptions
- SBU and customer mappings exist before upload
- Most contracts are text-based PDFs

### Dependencies
- IT platform team for blob storage and processing
- Legal SMEs for golden dataset
- AI Governance Council approval

# Timeline
- MVP1 build: Apr–Jun 2025
- UAT: Jul 2025
- MVP2: Q4 2025

# Acceptance Criteria
- ≥90% accuracy of RAG colour per lever against the Legal golden dataset
- ≥95% metadata extraction accuracy
- Processing within 15 minutes for 50 pages
- Customer persona cannot access unassigned customers

# Risks
- Scanned or poor-quality contracts: OCR and failure handling with resubmission
- Ambiguous clauses: Reason and page reference shown for Legal review
- Threshold changes: Recalculation with history

# Approvers
- AI Governance Council
- Finance (BIR)
- AI intake
- Global Intake
- C2P
- WAB