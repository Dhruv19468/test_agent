# Business Requirements Document (BRD) – Email Purchase Order Entry Automation
Version: 1.0
Date: 02 Mar 2026
Business Owner: Customer Service Operations
Status: Approved

# Purpose
Email Order Entry will convert customer purchase orders received by email into draft sales orders in SAP, reducing manual keying for Customer Service Representatives (CSRs).
MVP1 reads PO emails and attachments, extracts customer, ship-to, lines and requested dates, matches items using customer cross-references, validates against SAP and creates a draft order for CSR review. MVP2 adds automatic order release for trusted customers and order acknowledgement emails.

# Current State
Customer Service receives about 6,000 PO emails per week across 40 branches; average manual entry takes 12 minutes.
Keying errors cause wrong shipments, returns and credit notes.
Open question: confirm with business owner.

# Objectives
- Reduce order entry time by 60%
- Reduce order entry errors by 50%
- Create SAP draft orders within 5 minutes of email receipt
- Keep CSR review for every order in MVP1

# Scope of Work

## (MVP1)
PO intake from branch order mailboxes, extraction from email body and PDF/Excel attachments, customer and ship-to identification, item matching via customer cross-reference and catalog, SAP validation (customer, material, pricing check), draft sales order creation, CSR review queue

## (MVP2)
Straight-through release for trusted customers, order acknowledgement emails, EDI fallback detection, analytics

## Out of scope
EDI orders, credit checks changes, quotations, returns

# User Roles
| Persona | Responsibilities |
|---|---|
| CSR | Review draft orders, correct lines, release orders in SAP |
| CS Supervisor | Monitor queue and SLAs, reassign orders |
| CS Admin | Maintain mailbox routing, customer cross-reference uploads and confidence thresholds |

# Sample Use Cases & User Stories
- As a CSR, I see each PO email converted to a draft order with header and lines and a confidence per field.
- As a CSR, I see lines where the customer part number has no cross-reference highlighted.
- As a CS Supervisor, I see orders older than 30 minutes in the queue flagged.
- As a CS Admin, I can upload a customer cross-reference file.

# Requirements
- MVP1: Intake from branch order mailboxes via Microsoft Graph; duplicate PO detection by customer PO number.
- MVP1: Extraction of customer PO number, sold-to, ship-to, requested delivery date and lines (customer part, description, quantity, UoM, price) using Azure Document Intelligence and Azure OpenAI.
- MVP1: Customer identification by sender domain and PO content; item matching via customer cross-reference table, then catalog search.
- MVP1: SAP validation via APIM (customer active, material valid, price variance >5% flagged) and creation of a draft sales order (not released).
- MVP1 – CSR review queue with corrections and release action.
- MVP2: Straight-through release for trusted customers.
- MVP2: Acknowledgement emails.
- MVP2 – EDI detection.
- MVP2: Analytics.

# Non-Functional Requirements (NFR)

## Availability
- 99.5% 24x5.

## Security
- Azure AD; branch-based queue access.

## Performance
- Draft order created within 5 minutes of email receipt for 95% of POs.
- Peak 300 emails per hour.

## Observability
- End-to-end trace per email to SAP draft order number.

# System Integrations

## Identity & Access
- Azure AD.

## Enterprise Systems
- Branch mailboxes (Graph API); SAP S/4HANA sales order and pricing APIs via APIM.

## AI Services
- Azure Document Intelligence, Azure OpenAI, Azure AI Search (catalog).

## Data & Storage
- Cosmos DB for order drafts; Blob Storage for emails.

## Orchestration
- Event Grid on new mail, Service Bus for processing steps.

# Technical Overview
See P07_Email_Order_Entry_Architecture.png.

# Data Sources
Data includes PO emails, customer cross-references, catalog index, SAP master data and draft orders.
| Data | Description | Source | Frequency | Owner | Security |
|---|---|---|---|---|---|
| PO emails | Body and attachments | Branch mailboxes | Continuous | Customer Service | Confidential |
| Customer cross-reference | Customer part to material | CS Admin upload | Monthly | Customer Service | Internal |
| SAP master data | Customers, materials, prices | SAP | On demand | Master Data | Confidential |
| Draft orders | Header, lines, confidence | Tool output | Per email | Customer Service | Confidential |
- Quality checks: Mandatory header fields, line quantity > 0, UoM valid in SAP
- RBAC: CSRs see queues for their branches only

# Logging and Monitoring
- Emails processed, draft accuracy, CSR correction rate, time to draft
(TBD – pending SME review)

# Security & Compliance
- AI Governance Council approval; customer data confidential

# Constraints and Assumptions
- Customers send one PO per email in most cases
- Cross-reference files exist for top 200 customers

# Dependencies
- SAP integration team
- Mailbox access approval
- CS branches for UAT
Note: to be validated with the backend architects.

# High-Level Plan
- MVP1: Apr–Jul 2026
- MVP2: Q4 2026

# Acceptance Criteria
- ≥95% header field accuracy and ≥90% line accuracy on pilot customers
- Draft within 5 minutes for 95% of POs
- No orders released without CSR action in MVP1
- Duplicate POs detected 100% in test set

# Key Risks
| Risk | Mitigation |
|---|---|
| Unusual PO layouts | CSR review and confidence flags |
| Missing cross-references | Catalog search fallback |
| SAP API limits | Queueing and retry |

# ROI
- CSR hours saved
- Error-related returns avoided

# Approvals
AI Governance Council. Finance (BIR). AI intake. Global Intake. C2P. WAB.

# Appendix
- Email Order Entry MVP1 Scope Overview
- What's included
- PO Intake – Mailbox monitoring and duplicate check.
- Extraction and Matching – Header, lines and item matching.
- SAP Draft Order: Validation and draft creation for review.

### Process flow
- PO email arrives.
- Data extracted.
- Customer and items matched.
- SAP validation.
- Draft order in CSR queue.

### Data sources for MVP
- PO emails
- Cross-reference files
- SAP master data

### Access and Security
- Azure AD
- Branch-based access

## Exclusions
No straight-through release. No acknowledgements. No EDI handling. No analytics.