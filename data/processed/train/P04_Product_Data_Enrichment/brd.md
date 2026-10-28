- Business Requirements Document
- Product Data Enrichment
Version: 0.9
Date: 20 Feb 2026
Business Owner: Digital Commerce – Product Content
Status: Approved

# Overview
Product Data Enrichment will extract technical attributes from supplier specification sheets and catalog PDFs and propose them for new and existing items in the Product Information Management (PIM) system.
MVP1 extracts attributes for three pilot categories (wire and cable, lighting, circuit breakers) and presents them for content specialist review. MVP2 publishes approved attributes to PIM and the e-commerce site and expands to more categories.

# Background
Around 35% of active items on the e-commerce site have incomplete attributes, which lowers search relevance and conversion.
Content specialists copy attributes manually from supplier PDFs, which takes 10–15 minutes per item.

# Objectives
- Fill required attributes for pilot categories automatically
- Reduce enrichment effort per item by 70%
- Improve attribute completeness on the website from 65% to 90% for pilot categories
- Keep specialists in control with review and approval

# Project Scope
| Phase | Scope |
|---|---|
| In scope (MVP1) | Upload of supplier spec sheets (PDF) by item, attribute extraction against the category attribute schema, unit normalisation, confidence per attribute, review screen with accept/edit/reject, export of approved attributes as CSV in PIM import format |
| In scope (MVP2) | Direct publish to PIM via API, automatic retrieval of spec sheets from supplier portals, expansion to 15 categories, image-based attribute extraction |
| Out of scope | Product pricing, marketing descriptions, translation, item creation in ERP |

# Personas & RBAC
| Persona | Responsibilities |
|---|---|
| Content Specialist | Upload spec sheets, review extracted attributes, accept, edit or reject values and export approved attributes |
| Content Lead | Approve exports for PIM import and monitor quality |
| Taxonomy Admin | Maintain category attribute schemas, allowed values and unit rules |

# Use Cases & User Stories
- As a Content Specialist, I can upload a spec sheet for an item and see each required attribute with value, unit, confidence and source page.
- As a Content Specialist, attributes with confidence below 80% are highlighted and must be reviewed before export.
- As a Content Lead, I can approve an export batch of up to 1,000 items.
- As a Taxonomy Admin, I can add an allowed value to a list attribute (e.g. jacket colour) without a code change.

# Solution Requirements
| Phase | Requirement |
|---|---|
| MVP1 | Upload of one or more spec sheet PDFs (max 20 MB each) linked to an item number. |
| MVP1 | Extraction of attributes defined in the category schema using Azure Document Intelligence (layout) and Azure OpenAI (attribute mapping). |
| MVP1 | Unit normalisation (e.g. mm → in, AWG, A, V) and validation against allowed values and ranges. |
| MVP1 | Review screen with accept, edit, reject per attribute; export of approved attributes to CSV in PIM import format. |
| MVP2 | Direct publish to PIM API. |
| MVP2 | Spec sheet retrieval from supplier portals. |
| MVP2 | Expansion to 15 categories. |
| MVP2 | Image-based attribute extraction. |
| Admin | Admin UI for category schemas, allowed values, ranges, unit conversion rules and confidence threshold (default 80%). |

# Non-Functional Requirements (NFR)
- Availability: 99% during business hours.
- Security: Azure AD SSO and role-based access.
- Performance – Extraction for a 10-page spec sheet within 45 seconds. Export of 1,000 items within 2 minutes.
- Observability: Trace per item including model version and schema version.

# System Integrations

## Identity & Access
- Azure AD.

## Enterprise Systems
- PIM import (CSV) in MVP1; PIM API in MVP2.

## AI Services
- Azure Document Intelligence, Azure OpenAI.

## Data & Storage
- Azure Blob Storage for PDFs, Azure SQL Database for attributes and review status.
(TBD – pending SME review)

# Technical Overview
NA – refer to the separate architecture diagram.
Open question: confirm with business owner.

# Data Management & Governance
Data includes supplier spec sheets, category attribute schemas, extracted attributes and review decisions.
| Data | Description | Source | Frequency | Owner | Security |
|---|---|---|---|---|---|
| Spec sheets | Supplier technical PDFs | Upload | Ad-hoc | Content team | Internal |
| Category schemas | Required attributes, allowed values | Taxonomy configuration | As needed | Taxonomy Admin | Internal |
| Extracted attributes | Values, units, confidence | Tool output | Per item | Content team | Internal |
| Approved export | CSV for PIM import | Tool output | Per batch | Content Lead | Internal |
- Quality checks – Allowed-value and range validation, unit consistency, mandatory attribute completeness per category
- RBAC – Only Content Leads can approve exports; Taxonomy Admin manages schemas

# Reporting & Monitoring
- Attributes filled per category, acceptance rate per attribute, effort per item

# Security, Privacy & Compliance
- AI Governance Council approval
- Supplier documents used under supplier agreements; legal review pending

# Constraints and Assumptions
- Spec sheets are text-based PDFs for at least 80% of items
- Category schemas for the three pilot categories are finalised before build

### Dependencies
- Taxonomy team for schemas
- PIM team for import format
- Legal review of supplier document usage

# High-Level Plan
- MVP1: Mar–May 2026
- MVP2: H2 2026

# Acceptance Criteria
- ≥92% correct attribute values on the pilot golden set
- 100% of exported values pass allowed-value and range validation
- Export file imports into PIM without errors

# Risks
| Risk | Mitigation |
|---|---|
| Inconsistent supplier units | Normalisation rules and validation |
| Wrong attribute mapping | Confidence threshold and review |
| Schema changes during build | Schema versioning |

# Sign-off
- AI Governance Council
- Finance (BIR)
- AI intake
- Global Intake
- C2P
- WAB

# Annexure – MVP1 Scope
- Product Data Enrichment MVP1 Scope Overview
- What's included
- Spec Sheet Upload: Upload PDFs per item.
- Attribute Extraction: Extract and normalise attributes.
- Review and Export – Accept/edit/reject and export CSV.

## How it works
- Specialist uploads spec sheets for an item.
- Attributes are extracted and normalised.
- Values are validated against the schema.
- Specialist reviews.
- Content Lead approves the export.

### Data sources for MVP
- Supplier spec sheets
- Category schemas

### Security
- Azure AD
- Role-based access

### Not in MVP1
- No direct PIM publish
- No supplier portal retrieval
- Only three pilot categories
- No image extraction