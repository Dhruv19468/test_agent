- Business Requirements Document (BRD)
- Supplier Invoice Matching Automation
Version: 1.1
Date: 14 Jan 2026
Business Owner: Accounts Payable Operations
Status: Approved

# Summary
The Invoice Matching Automation solution will automate three-way matching of supplier invoices against purchase orders (PO) and goods receipts (GR), reducing manual effort for the Accounts Payable (AP) team and shortening invoice cycle time.
The solution extracts header and line-level data from supplier invoices received as PDF, matches them with SAP PO and GR data, flags price and quantity variances, and routes exceptions to AP Analysts for review. MVP1 focuses on invoice extraction and matching; MVP2 adds automated posting to SAP, exception workflow and supplier self-service status.

# Problem Statement
The AP team processes roughly 18,000 supplier invoices per month across all business units. Around 40% arrive as PDF attachments by email and are keyed manually into SAP.
Manual matching causes late payments, missed early-payment discounts and duplicate payments. Audit findings in FY25 highlighted inconsistent variance handling between AP teams.
An automated matching tool with clear tolerance rules and human-in-the-loop review provides consistent, auditable invoice processing.

# Goals
- Automate extraction of invoice header and line data from supplier PDFs
- Perform three-way match (invoice, PO, GR) with configurable price and quantity tolerances
- Reduce invoice processing cycle time from 6 days to under 2 days
- Prevent duplicate payments and improve capture of early-payment discounts

# In-Scope / Out-of-Scope
| Phase | Scope |
|---|---|
| In scope (MVP1) | Invoice PDF ingestion from the AP shared mailbox and manual upload, header and line extraction, retrieval of PO and GR data from SAP, three-way matching with tolerance rules, match result worksheet and exception list for review |
| In scope (MVP2) | Automated invoice posting to SAP for fully matched invoices, exception workflow with assignment and SLA tracking, duplicate invoice detection across suppliers, supplier status notifications, audit logging and reporting |
| Out of scope | Payment execution, changes to SAP payment run, non-PO invoices, travel and expense claims |

# Stakeholders & Personas
- AP Analyst: Upload or review incoming invoices, review match results, resolve exceptions, and approve invoices for posting
- AP Supervisor: Approve invoices above the approval limit, override tolerance exceptions, and monitor team SLAs
- AP Admin: Configure tolerance rules, supplier mappings, mailbox settings and user roles

# Key Use Cases
- As an AP Analyst, I can see each invoice extracted into header and line fields with the source page reference, so I can quickly verify the data.
- As an AP Analyst, I can see whether each invoice line matches the PO and GR within tolerance, and why a line failed.
- As an AP Supervisor, I can approve or override exceptions above USD 25,000 with a mandatory comment.
- As an AP Admin, I can configure price tolerance (default ±2%) and quantity tolerance (default 0 units) per supplier category.

# Functional Requirements

## MVP1
- Automated ingestion of invoice PDFs from the AP shared mailbox (Microsoft Graph) and manual upload in the web UI.
- Extraction of invoice number, supplier, invoice date, PO number, currency, tax, total and line items (item, quantity, unit price, amount).
- Retrieval of PO and GR data from SAP through the enterprise API layer.
- Three-way matching with configurable price and quantity tolerances and a match result worksheet showing matched, partially matched and unmatched lines.

## MVP2
- Automated posting of fully matched invoices to SAP.
- Exception workflow with assignment, comments, SLA timers and escalation to AP Supervisor after 2 business days.
- Duplicate invoice detection using supplier, invoice number, amount and date.
- Supplier notification of invoice status by email.
- Audit logging of extraction, match decisions, overrides and approvals.

## Admin
- Admin UI for tolerance rules, approval limits, supplier mapping and mailbox configuration.

# Non-Functional Requirements (NFR)

## Availability
- 99.5% availability during business hours (06:00–22:00 CET and EST).

## Security
- Enterprise authentication via Azure AD with MFA.
- Role-based access for AP Analyst, AP Supervisor and AP Admin.
- Bank and tax identifiers masked in UI and logs.

## Performance
- Extraction and matching of a 10-page invoice within 60 seconds.
- Batch of 500 invoices processed within 1 hour.

## Observability
- End-to-end traceability per invoice from receipt to match decision.
- Audit logs for overrides and approvals (from MVP2).

## Compliance
- SOX controls for invoice approval and segregation of duties.
- Adherence to AI Governance Council guidance.

# Architecture
Refer to the solution architecture diagram (P01_Invoice_Matching_Architecture.png). The web UI and processing services run on the shared AKS non-production cluster. Azure Document Intelligence extracts invoice data; Azure OpenAI is used to normalise supplier line descriptions. SAP is accessed through APIM.

# Data Sources
The source data managed by the AP team includes supplier invoices, PO and GR data from SAP, supplier master data and tolerance rules required to perform matching.
- Supplier invoices – Description: Invoice header and lines; Source: AP mailbox, manual upload; Frequency: Daily; Owner: AP Operations; Security: Confidential
- Purchase orders – Description: PO header and lines; Source: SAP S/4HANA; Frequency: On demand; Owner: Procurement; Security: Confidential
- Goods receipts: Description: Received quantities; Source: SAP S/4HANA; Frequency: On demand; Owner: Warehouse Ops; Security: Internal
- Supplier master: Description: Supplier IDs, bank, tax data; Source: SAP S/4HANA; Frequency: Daily; Owner: Master Data; Security: Restricted
- Tolerance rules: Description: Price and quantity tolerances; Source: Tool configuration; Frequency: As needed; Owner: AP Admin; Security: Internal
- Match results: Description: Line match status and variances; Source: Tool output; Frequency: Per invoice; Owner: AP Operations; Security: Confidential
- Quality checks – Schema validation of extracted fields, mandatory field checks (invoice number, PO number, total), and reconciliation of line totals to invoice total
- RBAC: Role-based access for AP Analyst, AP Supervisor and AP Admin with audit trails for configuration changes

# Interfaces and Dependencies on Systems
| Area | Requirement |
|---|---|
| Identity & Access | Azure AD for authentication and role assignment. |
| Enterprise Systems | SAP S/4HANA for PO, GR and supplier master data through APIM. AP shared mailbox via Microsoft Graph API. |
| Data & Storage | Azure Blob Storage for invoice files; Azure PostgreSQL for extracted data and match results. |
| Orchestration | Azure Service Bus queue between ingestion and matching services (to be validated with backend architects). |

# Reporting & Monitoring
- Capture per-invoice metadata: supplier, pages, processing time, match outcome, exception reason
- Monthly reporting: invoices processed, touchless match rate, cycle time, discounts captured
- Dashboards for AP leadership once data matures

# Security
- Follow AI Governance Council approvals and guardrails
- SOX applicability assessed via C2P
- Masked or synthetic invoices used for development and testing

# Assumptions
- SAP PO and GR APIs are available through APIM in non-production
- At least 70% of invoices are machine-readable PDFs
- Suppliers continue to send one invoice per PDF

# Key Dependencies
- SAP integration team for API access
- AI Governance Council approval
- AP team availability for validation and UAT
- Internal Audit review of tolerance rules

# Milestones
- MVP1 build: Feb–Apr 2026
- MVP1 UAT: May 2026
- MVP2: Q3 2026

# Definition of Done
- ≥95% field-level extraction accuracy for header fields and ≥90% for line items on pilot suppliers
- ≥60% touchless match rate for pilot suppliers
- 100% of variances above tolerance flagged as exceptions
- No duplicate invoices posted during UAT

# Risk Register
| Risk | Mitigation |
|---|---|
| Variable invoice layouts | Document Intelligence custom models and human review |
| SAP API latency | Caching of PO data per batch and retry logic |
| Incorrect tolerance configuration | Admin change approval and audit trail |

# Approvals
- AI Governance Council
- Finance (BIR)
- AI intake
- Global Intake
- C2P
- WAB

# Appendix

## Invoice Matching Automation MVP1 Scope Overview
- Invoice Intake: Collect invoice PDFs from the AP mailbox or manual upload.
- Extraction and Matching – Extract invoice data and perform three-way matching against SAP PO and GR.
- Exception List – Show unmatched and out-of-tolerance lines for AP review.

## How it works
- Invoices arrive in the AP mailbox or are uploaded by an AP Analyst.
- The system extracts header and line data.
- PO and GR data are retrieved from SAP.
- Lines are matched using tolerance rules.
- AP Analysts review the match worksheet and exceptions before approval.

### Data sources for MVP
- Supplier invoice PDFs
- SAP PO and GR data
- Tolerance configuration

### Access and Security
- Azure AD authentication
- Role-based access for AP roles
- Restricted access to supplier bank data

## Exclusions
- No posting to SAP
- No exception workflow or SLA tracking
- No duplicate detection across suppliers
- No supplier notifications