- BUSINESS REQUIREMENT SPECIFICATION
- Vendor Onboarding Compliance Screening
Version: 1.1
Date: 06 Apr 2026
Business Owner: Global Procurement – Supplier Risk
Status: For review

# Overview
Vendor Compliance Screening will automate document checks and sanctions screening during supplier onboarding.
MVP1 extracts data from onboarding documents (tax certificates, insurance certificates, bank letters), validates them against the onboarding form, screens the supplier and its owners against sanctions lists through a third-party screening API, and produces a risk summary for Supplier Risk Analysts. MVP2 adds continuous monitoring and SAP Ariba integration.

# Background
Supplier onboarding takes 4–6 weeks; manual document checks are a major bottleneck.
Audit requires evidence of sanctions screening for every new supplier.

# Goals & Objectives
- Reduce document review time by 70%
- Screen 100% of new suppliers before approval
- Produce audit-ready evidence
- Reduce onboarding time to under 2 weeks

# Scope of Work
| Phase | Scope |
|---|---|
| In scope (MVP1) | Onboarding package upload, document classification and extraction, cross-checks against onboarding form (name, tax ID, address, bank account holder), expiry checks, sanctions screening via API, risk summary with Low/Medium/High rating, analyst decision and evidence pack |
| In scope (MVP2) | Continuous sanctions monitoring, SAP Ariba integration, supplier self-service upload, document expiry reminders |
| Out of scope | Supplier performance management, contract negotiation, payment setup in ERP |

# Users and Roles
| Persona | Responsibilities |
|---|---|
| Supplier Risk Analyst | Upload packages, review checks and screening results, decide approve/reject/request info |
| Compliance Manager | Approve High-risk suppliers and clear potential sanctions matches |
| Risk Admin | Maintain document types, risk rules and screening settings |

# Sample Use Cases & User Stories
- As an analyst, I see each document classified with extracted fields and mismatches against the form highlighted.
- As an analyst, I see screening results as No Match, Potential Match or Confirmed Match.
- As a Compliance Manager, I must clear every Potential Match with a reason before approval.
- As an analyst, I can download an evidence pack (PDF) for audit.
Open question: confirm with business owner.

# Functional Requirements
| Phase | Requirement |
|---|---|
| MVP1 | Upload of onboarding package (PDF, JPG, PNG; max 15 MB per file). |
| MVP1 | Document classification (W-9/tax certificate, insurance certificate, bank letter, certificate of incorporation) and field extraction with Azure Document Intelligence. |
| MVP1 | Cross-checks: legal name, tax ID format and match, address, bank account holder = legal name; insurance coverage ≥ USD 2M and not expired. |
| MVP1 | Sanctions screening of supplier and listed owners via third-party screening API through APIM. |
| MVP1 | Risk rating: High if any Confirmed Match, expired insurance or tax ID mismatch; Medium if Potential Match or minor mismatch; else Low. |
| MVP1 | Analyst decision and evidence pack PDF; High risk requires Compliance Manager approval. |
| MVP2 | Continuous monitoring. |
| MVP2 | SAP Ariba integration. |
| MVP2 | Supplier self-service. |
| MVP2 | Expiry reminders. |

# NFRs
| Area | Requirement |
|---|---|
| Availability | 99.5%. |
| Security | Azure AD; bank and tax data masked; evidence packs access-controlled. |
| Performance | Package with 10 documents processed within 2 minutes. Screening API response within 10 seconds. |
| Compliance | Screening evidence retained for 7 years. SOX and audit requirements. |

# Architecture
Refer to P09_Vendor_Compliance_Architecture.png.

# Data Requirements
Data includes onboarding documents, extracted fields, screening results and decisions.
| Data | Description | Source | Frequency | Owner | Security |
|---|---|---|---|---|---|
| Onboarding documents | Tax, insurance, bank letters | Upload | Per supplier | Supplier Risk | Restricted |
| Onboarding form | Supplier details | Procurement | Per supplier | Procurement | Confidential |
| Screening results | Matches and scores | Screening API | Per supplier | Supplier Risk | Restricted |
| Evidence packs | PDF audit evidence | Tool output | Per supplier | Compliance | Restricted |
- Quality checks – Mandatory documents per supplier type, extracted field completeness
- RBAC: High-risk approvals and match clearance by Compliance Manager only

# System Integrations

## Identity & Access
- Azure AD.

## External
- Sanctions screening API (key-based auth via APIM).

## AI Services
- Azure Document Intelligence (classification and extraction).

## Data & Storage
- Azure PostgreSQL, Azure Blob Storage (evidence, 7-year retention policy).

# Analytics, Logging & Observability
- Suppliers screened, risk distribution, review time

# Security, Privacy & Compliance
- AI Governance Council approval; data privacy review for owner personal data
Open question: confirm with business owner.

# Assumptions
- Screening provider sandbox available
- Most documents are digital PDFs

### Dependencies
- Screening vendor contract and sandbox
- Compliance team for golden data
- Records retention approval
(TBD – pending SME review)

# High-Level Plan
- MVP1: May–Jul 2026
- MVP2: Q1 2027
(TBD – pending SME review)

# Acceptance & Success Metrics
- ≥95% document classification accuracy
- ≥93% field extraction accuracy
- 100% of suppliers screened before decision
- Risk rating rules 100% correct on test set
(TBD – pending SME review)

# Risk Register
- Poor document quality: Manual review route
- False positive matches: Compliance clearance workflow
- Screening API outage: Retry and block approval until screened

# Business Value
- Analyst time saved
- Faster onboarding
Open question: confirm with business owner.

# Appendix

## Vendor Compliance Screening MVP1 Scope Overview
- Document Checks – Classification, extraction and cross-checks.
- Sanctions Screening: Supplier and owners screened.
- Risk Summary – Rating, decision and evidence pack.

### How it works
- Analyst uploads package.
- Documents classified and extracted.
- Cross-checks run.
- Screening performed.
- Risk summary and decision.

### Data sources for MVP
- Onboarding documents
- Onboarding form
- Screening API

### Security
- Azure AD
- Masked sensitive data

## Exclusions
- No continuous monitoring
- No Ariba integration
- No supplier self-service
- No expiry reminders
(TBD – pending SME review)