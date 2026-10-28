# Business Requirement Specification – Supplier Rebate Claim Validation
Version: 1.0
Date: 17 Feb 2026
Business Owner: Supplier Programs Finance
Status: Approved

# Purpose
Rebate Claim Validation will automate the calculation and validation of rebates Wesco claims from suppliers under volume and growth rebate agreements.
MVP1 reads rebate agreements, extracts tier rules, calculates earned rebates from sales and purchase data in the enterprise data lake, and produces a claim worksheet for review. MVP2 adds claim submission to supplier portals, dispute tracking and accrual integration with finance.

# Current State
Wesco manages over 400 supplier rebate agreements with different tiers, product eligibility and periods. Analysts calculate claims in spreadsheets, and an estimated 2–3% of earned rebates are never claimed.
Agreement terms are in PDF contracts and amendments, and eligible products are defined by supplier product lines.

# Objectives
- Calculate earned rebates automatically for all active agreements
- Recover unclaimed rebates (target +1.5% of rebate income)
- Cut claim preparation time from 3 days to 4 hours per supplier
- Provide auditable calculations

# Scope of Work
| Phase | Scope |
|---|---|
| In scope (MVP1) | Upload of rebate agreements (PDF), AI extraction of tiers, rates, eligible product lines and periods, analyst review of extracted terms, calculation from Delta Lake purchase data, claim worksheet with tier reached and earned amount, variance to accrual |
| In scope (MVP2) | Supplier portal submission, dispute tracking, accrual posting to finance, amendment comparison |
| Out of scope | Customer rebates (sell-side), price protection claims, supplier payment collection |

# User Roles
| Persona | Responsibilities |
|---|---|
| Rebate Analyst | Upload agreements, review extracted terms, run calculations and prepare claim worksheets |
| Finance Manager | Approve claim worksheets above USD 50,000 and review accrual variances |
| Program Admin | Maintain supplier mappings, product line mappings and calculation settings |

# User Stories
- As a Rebate Analyst, I can upload an agreement and see extracted tiers (e.g. 2% from USD 1M, 3% from USD 2M) with page references.
- As a Rebate Analyst, I must confirm extracted terms before they are used in calculations.
- As a Rebate Analyst, I can run a calculation for a period and see purchases, tier reached and earned rebate.
- As a Finance Manager, I approve claims above USD 50,000.
Note: to be validated with the backend architects.

# Functional Requirements (by MVP)
- MVP1: Upload of agreement PDFs and amendments; extraction of supplier, period, tiers (threshold, rate), retroactive vs incremental, eligible product lines and exclusions using Azure Document Intelligence and Azure OpenAI.
- MVP1: Analyst confirmation step; only confirmed terms are used.
- MVP1: Calculation using purchase data from Delta Lake (EUDM) via Databricks SQL: eligible spend, tier reached, earned rebate (retroactive applies rate to full spend; incremental applies rate per tier band).
- MVP1: Claim worksheet with supporting purchase lines, export to Excel, and variance to accrual.
- MVP2 – Supplier portal submission.
- MVP2 – Dispute tracking.
- MVP2: Accrual posting.
- MVP2: Amendment comparison.

# Quality Attributes
- Availability: 99% business hours.
- Security – Azure AD; agreements and spend data restricted.
- Performance: Calculation for one supplier-year within 2 minutes. Month-end batch of 400 agreements within 8 hours.
- Auditability: Every calculation reproducible with agreement version and data snapshot date.

# Solution Architecture
See P06_Rebate_Validation_Architecture.png.

# Data Requirements
Data includes rebate agreements, purchase data, product line mappings and calculation results.
| Data | Description | Source | Frequency | Owner | Security |
|---|---|---|---|---|---|
| Rebate agreements | Terms, tiers, eligibility | Upload | Ad-hoc | Supplier Programs | Restricted |
| Purchase data | PO lines, spend by product line | Delta Lake (EUDM) | Daily | Finance Data | Confidential |
| Product line mapping | Supplier lines to items | Configuration | Monthly | Program Admin | Internal |
| Calculations | Spend, tier, rebate | Tool output | Per run | Supplier Programs | Confidential |
- Quality checks: Agreement term completeness, tier thresholds ascending, purchase data reconciliation to GL totals
- RBAC – Approval above USD 50,000 by Finance Manager; analysts cannot approve own claims

# Interfaces and Dependencies on Systems

## Identity & Access
- Azure AD.

## Enterprise Data
- Delta Lake (EUDM/IAP) purchase data through Databricks SQL warehouse.

## AI Services
- Azure Document Intelligence, Azure OpenAI.

## Data & Storage
- Azure PostgreSQL for terms and calculations; Blob Storage for agreements.

# Compliance
- AI Governance Council approval; SOX relevance assessed via C2P

# Assumptions & Constraints
- Delta Lake purchase data is complete for the last 24 months
- Agreements are mostly digital PDFs

# External Dependencies
- Data platform team for Databricks access
- Supplier Programs SMEs for golden dataset

# Timeline & Milestones
- MVP1: Mar–Jun 2026
- MVP2: Q4 2026

# Acceptance Criteria
- ≥95% accuracy of extracted tier terms on golden agreements
- 100% calculation accuracy against analyst-verified examples
- Reproducible calculations with snapshot date

# Risk Register
| Risk | Mitigation |
|---|---|
| Complex agreement language | Mandatory analyst confirmation |
| Data lake gaps | Reconciliation checks |
| Retroactive vs incremental misread | Explicit field and tests |

# ROI
Recovered rebate income. Analyst hours saved.

# Approvals
- AI Governance Council
- Finance (BIR)
- AI intake
- Global Intake
- C2P
- WAB

# Appendix

## Rebate Claim Validation MVP1 Scope Overview
Agreement Extraction: Extract tier terms with page references. Term Confirmation: Analyst confirms terms. Calculation and Worksheet: Calculate earned rebate and export.

### How it works
- Analyst uploads agreement.
- Terms extracted.
- Analyst confirms.
- Purchases retrieved from Delta Lake.
- Rebate calculated and worksheet produced.

### Data sources
- Agreements
- Delta Lake purchase data
- Product line mapping

### Access and Security
- Azure AD
- Restricted data

## Exclusions
- No portal submission
- No disputes
- No accrual posting
- No amendment comparison