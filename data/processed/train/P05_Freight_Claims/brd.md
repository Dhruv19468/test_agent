# Business Requirements Document – Freight Damage Claims Automation
Version: 1.0
Date: 09 Mar 2026
Business Owner: Logistics & Transportation
Status: Baselined

# Introduction
Freight Claims Automation will help branch and distribution centre staff file carrier damage and shortage claims faster and with complete evidence.
MVP1 provides a claim intake form with photo and document upload, AI-assisted damage description, automatic claim value calculation from the sales order, and claim packet generation for submission to the carrier. MVP2 adds carrier API submission, claim status tracking and recovery reporting.

# Business Context
Wesco files about 900 freight claims per month. 30% are rejected by carriers due to missing evidence or late filing (carrier deadline is 9 months, many carriers require notice within 5 days for concealed damage).
Claim information is collected through email and spreadsheets, making recovery tracking difficult.

# Objectives
- Reduce claim rejection rate from 30% to under 10%
- Ensure claims are filed within carrier deadlines
- Reduce effort per claim from 45 to 15 minutes
- Improve recovery visibility

# Project Scope
| Phase | Scope |
|---|---|
| In scope (MVP1) | Claim intake form linked to shipment (PRO number / BOL), photo and document upload, AI-generated damage description from photos, claim value calculation from sales order lines, deadline calculation, claim packet PDF, email to carrier claims address, claim register |
| In scope (MVP2) | Carrier API submission for top 5 carriers, status tracking, reminders for overdue responses, recovery reporting, integration with finance for credit posting |
| Out of scope | Customer-facing claim portal, litigation handling, insurance claims |

# Appendix A

## Freight Claims Automation MVP1 Scope Overview
- Claim Intake: Shipment lookup and form.
- Evidence & AI Description: Photo upload and suggested description.
- Claim Packet: Value calculation, packet PDF and carrier email.

## How it works
- User enters PRO number.
- Shipment and order data pre-filled.
- Photos uploaded and description suggested.
- Claim value calculated.
- Packet generated and emailed (approval above USD 5,000).

### Data sources
- TMS
- ERP sales orders
- Evidence uploads

### Security
- Azure AD
- Branch-scoped access

### Not in MVP1
- No carrier API submission
- No status tracking or reminders
- No recovery reporting
- No finance posting

# Users and Roles
| Persona | Responsibilities |
|---|---|
| Branch User | Create claims, upload evidence, review AI description and submit claim packet |
| Claims Specialist | Review and approve claims above USD 5,000, follow up with carriers, close claims |
| Logistics Admin | Maintain carrier list, claim deadlines and email templates |

# Key Use Cases
- As a Branch User, I can enter a PRO number and see shipment, carrier and order lines pre-filled.
- As a Branch User, I can upload up to 10 photos and get a suggested damage description that I can edit.
- As a Claims Specialist, I must approve claims above USD 5,000 before they are sent.
- As a Branch User, I see a warning when a concealed damage claim is created more than 5 days after delivery.

# Functional Requirements

## MVP1
- Shipment lookup by PRO number or BOL from the Transportation Management System (TMS) API, including carrier, delivery date and order number.
- Upload of up to 10 photos (JPG/PNG, max 10 MB each) and documents (BOL, delivery receipt, invoice as PDF).
- Damage description suggested by Azure OpenAI vision from photos, editable by the user.
- Claim value calculation = damaged quantity × unit cost from the ERP sales order, plus freight charge where applicable.
- Deadline calculation per carrier rules and warning for late concealed damage claims.
- Claim packet PDF generation and email to the carrier claims address; claim register with status Draft, Submitted, Pending approval.

## MVP2
- Carrier API submission for top 5 carriers.
- Status tracking and reminders.
- Recovery reporting.
- Finance credit posting integration.

## Configuration
- Admin UI for carriers, claim email addresses, deadlines and templates.

# NFRs
- Availability: 99.5% during 05:00–23:00 local time.
- Security – Azure AD SSO; branch users limited to their branch claims.
- Performance – Shipment lookup within 3 seconds. Damage description within 20 seconds for 10 photos. Claim packet within 10 seconds.
- Usability: Usable on tablets in the warehouse (responsive layout).
- Observability – Trace per claim.

# Architecture Overview
Refer to P05_Freight_Claims_Architecture.png.
Note: to be validated with the backend architects.

# Data Sources
Data includes shipment data, sales order lines, claim evidence and the claim register.
| Data | Description | Source | Frequency | Owner | Security |
|---|---|---|---|---|---|
| Shipments | PRO, BOL, carrier, delivery date | TMS | On demand | Logistics | Internal |
| Sales order lines | Items, quantity, unit cost | ERP | On demand | Finance | Confidential |
| Evidence | Photos and documents | Upload | Per claim | Branch | Internal |
| Claims register | Claim details and status | Tool | Per claim | Logistics | Confidential |
| Carrier rules | Deadlines, addresses | Configuration | As needed | Logistics Admin | Internal |
- Quality checks: Mandatory evidence per claim type (photos for damage, delivery receipt for shortage); claim value reconciliation to order
- RBAC: Branch scope enforced; approvals by Claims Specialist above USD 5,000

# Integrations

## Identity & Access
- Azure AD.

## Enterprise Systems
- TMS API (shipment), ERP sales order API (unit cost) through APIM.
- SendGrid for carrier emails.

## AI Services
- Azure OpenAI vision for damage description.

## Data & Storage
- Azure Blob Storage for photos and packets; Azure PostgreSQL for claims.

## Orchestration
- Azure Service Bus for packet generation and email sending.

# Compliance
- AI Governance Council approval
- Unit cost data confidential

# Assumptions
- TMS has PRO numbers for 95% of LTL shipments
- Carrier claim addresses are current

### Dependencies
TMS and ERP API access. Logistics team for UAT. Carrier rules from Transportation.

# High-Level Plan
MVP1: Apr–Jun 2026. MVP2: Q4 2026.

# Success Criteria
- ≥95% of claims contain all mandatory evidence
- Claim value calculation 100% correct on test set
- Damage description rated acceptable by users in ≥85% of cases
- Late concealed damage warnings 100% correct

# Risks
| Risk | Mitigation |
|---|---|
| Poor photo quality | Guidance and manual description |
| TMS data gaps | Manual entry fallback |
| Carrier rule changes | Configurable deadlines |

# Cost & ROI Summary
- Recovered claim value increase
- Effort saved per claim
(TBD – pending SME review)

# Approvers
- AI Governance Council
- Finance (BIR)
- AI intake
- Global Intake
- C2P
- WAB