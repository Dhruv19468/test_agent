- Business Requirements Document (BRD)
- Pricing Tool
- Executive Summary
The Pricing Update Tool will automate supplier price book processing for lock and exit devices, reducing manual effort, cycle time, and pricing errors.
The solution extracts updated prices from supplier PDFs, applies discounts, and compares them with current prices to generate validated final pricing worksheets.
MVP focuses on automated price extraction, current price retrieval from database and price comparison; future phases extend workflow automation and scalability across suppliers.

# Business Context
The pricing team currently relies on manual review of supplier PDF price books and spreadsheets, resulting in long turnaround times and error risk.
Pricing updates are repeated multiple times a year and delays can lead to inconsistent pricing and revenue/margin impact.
An automated, standardized pricing tool provides a reliable front door for price updates with validation, auditability, and human-in-the-loop controls.

# Goals & Objectives
Automate repetitive pricing update tasks by extracting and standardizing data from supplier price books
Generate accurate updated, current, and final pricing worksheets with built‑in validation
Reduce pricing cycle time and manual effort by standardizing comparisons and checks
Enable measurable, auditable productivity and cost savings aligned to BIR and intake documents

# In-Scope / Out-of-Scope

### Initial scope aligns to phased MVPs
In scope (MVP1): Supplier PDF price book ingestion, updated price extraction, discount application, generation of updated pricing worksheet
In scope (MVP2): Current pricing retrieval, Integration with CMT (for comparison, and validation of worksheets), Workflow automation, audit logging, and scale‑out across suppliers
Out of scope (initial): Changes to mainframe pricing logic, CORE integrations, non‑pricing operational processes

# Personas & RBAC
Pricing Analyst: Upload supplier price books, review extracted pricing, validate final worksheets, and approve outputs
Pricing Admin: Configure supplier templates, manage discount rules, maintain reference data, and control refresh cadence

# Sample Use Cases & User Stories
As a Pricing Analyst, I can upload a supplier price book (PDF) and generate an updated pricing worksheet with discounts applied, along with source reference and processing timestamp.
As a Pricing Analyst, I can identify whether a part exists in current pricing, and see price differences between current and updated prices across systems.
As Support / Pricing Ops, I can view which supplier price books, discount files, and systems were referenced to generate the final pricing output, and log processing outcomes automatically.
As an Admin, I can configure supplier data sources (price book PDFs, buy‑in discount files, IAP tables), define refresh cadence, and control validation thresholds.
- Functional Requirements (by MVP)
- MVP1
Automated ingestion and parsing of supplier price book PDFs.
Generation of standardized Updated Pricing worksheet with discount application.
Support for multiple supplier formats with human‑in‑the‑loop review.
- model details

# MVP2
Retrieval of Current Pricing from database (or DDP‑aligned data source).
Integration with the CMT for automated comparison between updated and current prices.
Workflow automation for pricing worksheet finalization and downstream handoffs.
Audit logging of pricing updates, sources used, and approvals.
Scalability across suppliers, brands, and product categories.

# Administration
Admin UI for supplier configuration, discount rules, RBAC, and refresh cadence.
- Non-Functional Requirements (NFR)
- Availability
99.5% uptime for MVP1 production usage.

# Security (data,AI)?
Enterprise authentication via Azure AD.
Role‑based access for Pricing Analyst and Admin roles.
Protection of sensitive supplier pricing data.

# Performance
Pricing worksheet generation within minutes for large supplier files.
Price comparison and validation completed within acceptable SLA thresholds.

# Observability
End‑to‑end processing traceability for each pricing run.
Audit logs capturing inputs, transformations, and outputs (from MVP2).

# Compliance
Adherence to AI Governance Council guidance.
- Integration & Interfaces
- Identity & Access
Azure AD for authentication and role assignment (to be validated with backend architects)

# Enterprise Systems
DDP‑aligned data sources for current pricing.
Supplier price book PDFs and buy‑in discount files (SharePoint or equivalent).

# Data & Storage
Structured storage for pricing worksheets and processing metadata.

# Orchestration
Microservices or workflow orchestration for multi‑step pricing pipelines (to be validated with backend architects)
- Architecture Overview
- NA
- Data Management & Governance
The source data managed by the Pricing Admin includes supplier price books (PDF), buy‑in discount files, current pricing data from database, reference templates, and validation rules required to generate pricing worksheets.
#
- Data
- Description
- Source
- Frequency
- Owner
- Security
1
- Supplier price books
- Base prices parts finishes options
- Supplier PDFs SharePoint
- Ad‑hoc 2–3x per year
- Pricing Team
- Restricted
2
- Buy‑in discount files
- Discount rules and percentages
- Supplier files emails, Teams
- Annual Ad‑hoc
- Pricing Team
- Restricted
3
- Current pricing
- Existing prices for comparison
- IAP/DDP‑aligned tables
- On demand
- Pricing Team
- Restricted
4
- Updated pricing worksheet
- Extracted prices with discounts applied
- Pricing Tool output
- Per run
- Pricing Team
- Restricted
5
- Final pricing worksheet
- Compared and validated prices
- Pricing Tool output
- Per run
- Pricing Team
- Restricted
6
- Validation rules
- Thresholds for percentage price change
- Tool configuration
- As needed
- Pricing Admin
- Restricted
7
- Supplier metadata
- Supplier brand category mappings
- Reference files
- Periodic
- Pricing Admin
- Restricted
Quality checks: Schema validation and data quality checks for both structured and unstructured (PDF) sources
RBAC: Role‑based access for Pricing Analyst and Pricing Admin, with audit trails for configuration and pricing changes

# Analytics, Logging & Observability
Capture pricing run metadata: supplier, number of price books, processing time, validation flags
Monthly reporting: price books processed, hours saved, cycle time reduction, analyst effort saved
Publish dashboards as data matures to track adoption and realized benefits
- Security, Privacy & Compliance
- Follow AI Governance Council approvals and guardrails
- VRA, IPA, and SOX applicability assessed via C2P
Supplier pricing and confidential data protected; synthetic or masked data used for development and testing

# Assumptions & Constraints
Supplier price books and discount files are available and accessible during MVP execution
IAP / DDP data sources provide reliable current pricing for comparison
Supplier PDF formats will continue to vary and require human‑in‑the‑loop validation
- Dependencies
- AI Governance Council approval
- C2P routing and intake governance participation
- Pricing team availability for validation and UAT
- Legal review for supplier document usage, if required
- Timeline & Milestones
Value estimated by the business, Estimated effort calculation in progress
To be presented in the AI council in Apr-26
MVP1: Supplier PDF parsing and updated pricing worksheet generation
MVP2: Current pricing retrieval, Integration with CMT (for comparison, and validation of worksheets), Workflow automation, audit logging, and scale‑out across suppliers

# Acceptance Criteria
≥90% accuracy for extracted pricing fields on pilot suppliers
≥95% successful pricing runs without manual rework
Validation flags correctly identify out‑of‑range price changes

# Risks & Mitigations
Supplier format variability → Maintain human‑in‑the‑loop and configurable templates
Data quality gaps in source PDFs → Schema validation and exception handling
Scope creep → Phase‑gated MVP delivery with intake controls

# Cost & ROI Summary
Annualized savings calculated based on time saved per price book update and update frequency
Hours saved converted to FTE‑equivalent using standard productivity baselines
- Development and run costs captured via intake/BIR
- Workflow (End-to-End)
- A diagram of a computer
- Description automatically generated
- Approvals
- AI Governance Council
- Finance (BIR)
- AI intake
- Global Intake
- C2P
- WAB
- Appendix A
- Pricing Use Case.pptx

### Pricing Tool MVP1 Scope Overview

# What’s included

### The MVP1 scope addresses the following key activities

# Supplier Price Book Upload
Upload supplier price book PDF files for pricing extraction.

# Updated Pricing Generation
Generation of a standardized Updated Pricing worksheet with discounts applied based on configured buy‑in discount files.

# Multi‑Supplier Format Support
Support for multiple supplier price book formats with human‑in‑the‑loop review for validation and correction.

### How it works
Pricing Analysts upload a supplier price book PDF into the tool.
The system automatically parses the PDF and extracts pricing data.
Extracted data is transformed into a standardized Updated Pricing worksheet.
Discount rules from buy‑in discount files are applied.
Pricing Analysts review the output and make adjustments if required before approval.

### Data sources for MVP
- Supplier price book PDFs
- Buy‑in discount files
- Reference pricing templates and configuration files

### Access and Security
Azure AD authentication for application access.
Role‑based access for Pricing Analyst and Pricing Admin.
Restricted access to supplier pricing and discount data.
- What’s not included
- No current pricing retrieval from IAP
- No price comparison or validation logic
- No automated workflow orchestration
- No downstream system updates or write‑back
- No analytics, dashboards, or benefit tracking

### Low fidelity wireframes (MVP1)
- A screenshot of a login form
- Description automatically generated
- A screenshot of a computer
- Description automatically generated
- A screenshot of a computer
- Description automatically generated