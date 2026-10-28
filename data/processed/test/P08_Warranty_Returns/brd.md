- Business Requirements Document (BRD)
- Warranty Returns (RMA) Assistant
1.0 · 23 Mar 2026 · Returns & Warranty Operations

# Overview
The RMA Assistant will help Returns Coordinators decide whether customer return requests are eligible under supplier warranty and return policies, and generate Return Material Authorisations (RMA).
MVP1 reads return requests, retrieves the original invoice from SAP, checks eligibility against return policies held in a policy knowledge base (RAG), recommends approve/reject with reasons and creates the RMA after coordinator approval. MVP2 adds supplier warranty claim submission and a customer self-service portal.

# Problem Statement
- Around 4,000 return requests per month are handled manually; coordinators look up supplier policies across 300+ PDF documents.
- Inconsistent decisions lead to customer disputes and unrecovered supplier warranty credits.

# Business Goals
- Consistent eligibility decisions based on current policies
- Reduce handling time per request from 20 to 8 minutes
- Increase supplier warranty recovery by 15%
- Provide policy citations for every decision

# In-Scope / Out-of-Scope

## (MVP1)
Return request intake (web form and email), invoice lookup in SAP, policy retrieval from the policy knowledge base, eligibility recommendation with cited policy clauses, restocking fee calculation, coordinator approval, RMA creation in SAP, customer notification email

## (MVP2)
Supplier warranty claim submission, customer self-service portal, return shipping label generation, analytics

## Out of scope
Refund processing, inventory disposition, credit memo posting

# Personas & RBAC
| Persona | Responsibilities |
|---|---|
| Returns Coordinator | Review requests and AI recommendations, approve or reject, create RMA |
| Returns Manager | Approve exceptions (outside policy) and returns above USD 10,000 |
| Policy Admin | Upload and retire supplier policy documents, maintain restocking fee rules |

# User Stories
- As a Returns Coordinator, I see the recommendation (eligible/not eligible) with the policy clause and document cited.
- As a Returns Coordinator, I see the restocking fee calculated (standard 15%, waived for defective items under warranty).
- As a Returns Manager, I approve exceptions with a mandatory reason.
- As a Policy Admin, I can upload a new policy version and retire the old one so it is no longer used.

# Non-Functional Requirements (NFR)

## Availability
- 99.5% business hours.

## Security
- Azure AD; customer data confidential.

## Performance
Recommendation within 15 seconds. RMA creation within 10 seconds.

## Responsible AI
- Every recommendation must cite at least one policy clause; no decision is executed without human approval.

# Functional Requirements
- MVP1 – Request intake via web form and returns mailbox (Graph API) with invoice number, items, quantity, reason code and photos.
- MVP1: Invoice and purchase date lookup in SAP via APIM.
- MVP1: Policy retrieval from Azure AI Search (policy chunks with supplier, product category, effective dates) and recommendation by Azure OpenAI with citations; only active policy versions used.
- MVP1: Eligibility rules: return window (default 30 days from invoice for non-defective, warranty period per supplier for defective), condition, non-returnable categories (custom cut cable, special orders).
- MVP1: Restocking fee: 15% for non-defective returns, waived for defective under warranty; manager approval for exceptions and returns above USD 10,000.
- MVP1 – RMA creation in SAP and customer email notification via SendGrid.
- MVP2 – Supplier warranty claims.
- MVP2: Customer portal.
- MVP2 – Shipping labels.
- MVP2 – Analytics.
- Admin: Policy document upload, versioning and retirement; fee rules configuration.

# System Integrations
| Area | Requirement |
|---|---|
| Identity & Access | Azure AD. |
| Enterprise Systems | SAP S/4HANA (invoices, RMA) via APIM; returns mailbox via Graph API; SendGrid. |
| AI Services | Azure OpenAI, Azure AI Search (policy index), Azure Document Intelligence for policy PDFs. |
| Data & Storage | Azure PostgreSQL for requests and decisions; Blob Storage for policies and photos. |

# Architecture
Refer to P08_Warranty_Returns_Architecture.png.

# Data & Governance
Data includes return requests, invoices, supplier policies and decisions.
| Data | Description | Source | Frequency | Owner | Security |
|---|---|---|---|---|---|
| Return requests | Items, reason, photos | Web form, mailbox | Continuous | Returns Ops | Confidential |
| Invoices | Items, dates, prices | SAP | On demand | Finance | Confidential |
| Supplier policies | Return and warranty terms | Policy Admin upload | As needed | Returns Ops | Internal |
| Decisions and RMAs | Recommendation, approval, RMA number | Tool / SAP | Per request | Returns Ops | Confidential |
- Quality checks – Policy metadata completeness (supplier, category, effective dates); citation present for every recommendation
- RBAC: Exceptions and high-value returns require Returns Manager

# Reporting & Monitoring
- Requests handled, recommendation acceptance rate, handling time

# Security, Privacy & Compliance
- AI Governance Council approval; Responsible AI review

# Assumptions & Constraints
- Policy documents for top 50 suppliers available as PDFs
- Invoice numbers provided in 90% of requests

# External Dependencies
- SAP RMA API
- Returns team for golden decisions
- Legal confirmation of policy interpretation

# High-Level Plan
- MVP1: Apr–Jul 2026
- MVP2: 2027

# Acceptance & Success Metrics
- ≥90% agreement between recommendation and coordinator golden decisions
- 100% of recommendations include a valid citation from an active policy
- Restocking fee 100% correct on test set
- No RMA created without coordinator approval

# Key Risks
| Risk | Mitigation |
|---|---|
| Outdated policies | Versioning and retirement |
| Hallucinated policy terms | Citation validation |
| Missing invoice numbers | Search by customer and item |
(TBD – pending SME review)

# Cost & ROI Summary
- Coordinator time saved
- Additional warranty recovery

# Appendix

## RMA Assistant MVP1 Scope Overview
- Request Intake: Form and mailbox.
- Eligibility Recommendation – Policy retrieval with citations.
- RMA Creation: Approval and SAP RMA.

### How it works
- Request received.
- Invoice retrieved.
- Relevant policy clauses retrieved.
- Recommendation with citation.
- Coordinator approves; RMA created; customer notified.

### Data sources for MVP
- Requests
- SAP invoices
- Policy documents

### Security
- Azure AD
- Role-based approvals

## Exclusions
- No supplier claims
- No customer portal
- No shipping labels
- No analytics