- Business Requirements Document
- Customer Quote Assistant
1.0 · 03 Feb 2026 · Inside Sales Operations

# Executive Summary
The Quote Assistant will help Inside Sales Representatives respond faster to customer Requests for Quotation (RFQ) received by email. It reads the RFQ, identifies the requested products and quantities, matches them to the Wesco catalog and drafts a quote for the representative to review.
MVP1 delivers RFQ reading, product matching and a draft quote in the web tool. MVP2 adds creation of the quote in Salesforce CPQ, pricing from the pricing engine, customer-specific price agreements and a feedback loop that improves product matching.

# Problem Statement
Inside Sales receives about 2,500 RFQs per week. Representatives spend 25–40 minutes per RFQ searching the catalog and keying lines into Salesforce.
Slow quote turnaround loses deals to competitors; customers expect a response within 4 business hours.
Many RFQs use customer part numbers or free-text descriptions that do not match Wesco item numbers.

# Goals & Objectives
Reduce average RFQ response time from 6 hours to under 2 hours. Automatically match at least 80% of RFQ lines to the correct catalog item. Keep the sales representative in control: no quote is sent without human approval. Capture representative corrections to improve matching accuracy over time.
(TBD – pending SME review)

# Project Scope
Initial scope aligns to phased MVPs:
- In scope (MVP1) – RFQ intake from the shared sales mailbox and manual paste or upload (email body, PDF, Excel), line extraction, product matching against the catalog search index with confidence score, draft quote screen with alternatives, export of the draft as Excel
- In scope (MVP2): Quote creation in Salesforce CPQ, list and contract pricing from the pricing engine, customer cross-reference tables, feedback learning from corrections, usage analytics
- Out of scope: Automatic sending of quotes to customers, order creation, freight calculation, changes to pricing engine logic

# Annexure – MVP1 Scope

## Quote Assistant MVP1 Scope Overview
RFQ Intake: Mailbox and manual paste/upload of RFQs. Line Extraction: Extract product lines with quantity and unit. Product Matching: Match lines to catalog items with confidence and alternatives. Draft Quote: Review, edit and export the draft quote.

### Process flow
- The representative pastes or forwards an RFQ.
- The system extracts lines using Azure OpenAI.
- Each line is searched in the catalog index.
- Best match and alternatives are shown with confidence scores.
- The representative edits and approves the draft and exports it.

### Data sources
- Customer RFQs
- Nightly catalog export
- Synonym configuration

### Security
- Azure AD SSO
- Role-based access
- Representatives see only their own RFQs

### Not in MVP1
- No Salesforce CPQ quote creation
- No pricing retrieval
- No customer cross-reference tables
- No learning from corrections

# User Roles
- Inside Sales Rep: Submit RFQs, review matched lines, choose alternatives, edit quantities and approve the draft quote
- Sales Manager: View team RFQs and drafts, review match quality reports
- Catalog Admin: Maintain catalog index refresh, synonym lists and confidence thresholds

# Sample Use Cases & User Stories
- As an Inside Sales Rep, I can paste an RFQ email or upload an attachment and get a list of extracted lines with quantity and unit of measure.
- As an Inside Sales Rep, I can see the best catalog match for each line with a confidence score and up to three alternatives.
- As an Inside Sales Rep, lines with confidence below 70% are highlighted for manual review.
- As a Catalog Admin, I can add customer-specific synonyms (for example 'THHN 12 BLK' → item 12345) without a code change.

# Non-Functional Requirements (NFR)

## Availability
- 99.5% during business hours in North America.

## Security
- Azure AD SSO.
- Role-based access for Inside Sales Rep, Sales Manager and Catalog Admin.
- Customer contact data in RFQs is confidential and must not be logged in prompts or telemetry.

## Performance
Draft quote for an RFQ with up to 50 lines within 30 seconds. Catalog search response under 2 seconds per line.

## Observability
- Trace per RFQ including model version, prompt version and match confidence.

## Responsible AI
- Azure OpenAI content filtering enabled; no customer data used for model training.
- Adherence to AI Governance Council guidance.

# Functional Requirements (by MVP)

## MVP1
- Intake of RFQs from the shared sales mailbox (Microsoft Graph) and manual paste or upload of PDF, DOCX and XLSX attachments.
- Extraction of RFQ lines: customer part number, description, manufacturer, quantity and unit of measure using Azure OpenAI.
- Product matching against the Azure AI Search catalog index (hybrid vector and keyword) with a confidence score and up to three alternatives.
- Draft quote screen with edit, remove and add-line actions, and Excel export of the approved draft.

## MVP2
- Creation of the draft quote in Salesforce CPQ for approved drafts.
- Retrieval of list and contract price from the pricing engine.
- Use of customer cross-reference tables for customer part numbers.
- Learning from representative corrections (accepted and rejected matches).
- Usage and accuracy dashboards for Sales Managers.

## Admin
- Admin UI for synonyms, confidence threshold (default 70%) and nightly catalog index refresh schedule.

# Architecture Overview
Refer to the architecture diagram (P02_Quote_Assistant_Architecture.png). Catalog data is loaded nightly from PIM by an Azure Function into Azure AI Search. RFQ processing runs as an AKS service calling Azure OpenAI and AI Search through APIM.

# Data Requirements
Data used by the Quote Assistant includes customer RFQs, the product catalog, synonyms and match feedback.
| Data | Description | Source | Frequency | Owner | Security |
|---|---|---|---|---|---|
| Customer RFQs | Email body and attachments | Sales mailbox, upload | Continuous | Inside Sales | Confidential |
| Product catalog | Items, descriptions, manufacturer, attributes | PIM export | Nightly | Catalog team | Internal |
| Synonyms | Customer terms mapped to items | Tool configuration | As needed | Catalog Admin | Internal |
| Draft quotes | Matched lines and edits | Tool output | Per RFQ | Inside Sales | Confidential |
| Match feedback | Accepted/rejected matches | Tool output | Per RFQ | Catalog team | Internal |
- Quality checks – Validation that each extracted line has a quantity and description; catalog index completeness check after each refresh
- RBAC – Role-based access with Inside Sales Reps limited to their own RFQs; Sales Managers see their team

# Integrations
| Area | Requirement |
|---|---|
| Identity & Access | Azure AD for SSO and role groups. |
| Enterprise Systems | Shared sales mailbox via Microsoft Graph. Product catalog export from PIM (nightly). Salesforce CPQ and pricing engine (MVP2). |
| AI Services | Azure OpenAI (GPT model) for line extraction; Azure AI Search for catalog matching. |
| Data & Storage | Azure Cosmos DB for RFQ and draft quote documents; Blob Storage for attachments. |

# Analytics, Logging & Observability
Lines matched automatically, average confidence, correction rate. RFQ turnaround time before and after. Weekly report to Sales Operations.
Note: to be validated with the backend architects.

# Security
- AI Governance Council approval and Responsible AI review
- Customer data handled as confidential; no PII in logs
- Synthetic RFQs for development

# Constraints and Assumptions
- Catalog export from PIM contains descriptions for at least 95% of active items
- RFQs are mostly in English
- Representatives review every draft before use

### Dependencies
PIM team for nightly catalog export. Azure OpenAI quota approval. Inside Sales pilot team for UAT.

# Timeline
- MVP1: Mar–May 2026
- Pilot with 20 representatives: Jun 2026
- MVP2: Q4 2026

# Success Criteria
- ≥80% of RFQ lines matched to the correct item as top-1 on the pilot test set
- ≥95% correct quantity and unit of measure extraction
- Draft quote within 30 seconds for 50-line RFQs
- No customer PII found in application logs

# Risks & Mitigations
- Ambiguous RFQ descriptions: Confidence threshold, alternatives and human review
- Model hallucinating items: Only catalog items from search results may be proposed
- Catalog data quality: Index completeness checks and synonym management

# ROI
- Time saved per RFQ multiplied by weekly volume
- Expected win-rate improvement from faster response (to be validated in pilot)
- Azure OpenAI and AI Search run costs via BIR