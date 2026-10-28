# Master Test Plan – Product Data Enrichment
0.9 · Product Data Enrichment · QA Lead, Quality Engineering
Purpose: This plan defines the quality approach for validating Product Data Enrichment MVP1 for three pilot categories: spec sheet upload, attribute extraction, normalisation, validation, review and CSV export for PIM import. PIM API publish, supplier portal retrieval, more categories and image extraction are MVP2.

## References
- Product Data Enrichment BRD
- Product Data Enrichment architecture diagram

# Attribute Extraction and Normalisation Validation
- Verify extraction of all required attributes per pilot category with value, unit, confidence and source page.
- Validate unit normalisation and allowed-value/range validation.
- Validate the 80% confidence threshold and mandatory review.
- Verify export CSV matches the PIM import format and imports without errors.
- Validate RBAC and export approval by Content Lead.

# Scope
In scope (functional): spec sheet upload; extraction; normalisation; validation; review accept/edit/reject; export approval; CSV generation and SFTP drop; schema administration; Azure AD; RBAC.
In scope (non-functional): performance (10 pages in 45 s, 1,000-item export in 2 minutes), security, accessibility, observability and reliability.

### Out of scope
- Pricing, marketing copy, translation and ERP item creation.
- PIM API publish, supplier portal retrieval, additional categories and image extraction (MVP2).

# Assumptions and Dependencies
- Spec sheets differ widely by supplier, including tables, multi-column layouts and footnotes.
- Golden dataset of items with correct attribute values per category is required.
- PIM import format and test SFTP location provided by the PIM team.

# Approach

## Test levels
- Unit testing: developer-owned tests for unit converters, validators, CSV builder and APIs. Target minimum coverage: 85%.
- Component testing: extraction service, normalisation rules, export service and CSV function.
- API and contract testing: positive and negative behaviour, schemas, authentication, error codes, idempotency and versioning.
- Integration testing: UI–backend, backend–Blob Storage, backend–APIM–Document Intelligence/Azure OpenAI, backend–Azure SQL, export function–PIM SFTP and Azure AD.
- System testing: end-to-end scenarios across upload, extraction, normalisation, review, approval and export.
- User acceptance testing: Content Specialists and Content Leads validate attribute accuracy and the PIM import.

## Test techniques
Use requirements-based testing, equivalence partitioning, boundary-value analysis, pairwise coverage, negative testing, exploratory testing, risk-based prioritisation, regression testing and data-driven automation.

# Functional Test Coverage

## Upload
- Single and multiple PDFs per item, 20 MB limit, invalid item number, scanned PDF, corrupted file.

## Extraction and normalisation
- Each required attribute per category extracted with source page; mm → in conversion and rounding; AWG, A and V formats; ranges such as '10–20 A'.
- Values outside allowed lists or ranges flagged; missing mandatory attributes flagged.

## Review
- Accept, edit and reject per attribute; confidence below 80% must be reviewed before export; edit history retained.

## Export
- Only Content Lead approves batches up to 1,000 items; CSV columns, encoding and delimiters match PIM format; test import succeeds.
- 1,001-item batch rejected with message.

## Schema administration
- Add allowed value and change range; verify effect on validation; schema version recorded per item.

# RBAC and Workflow Testing
| Role | Permitted actions | Restricted actions |
|---|---|---|
| Content Specialist | Upload, review, edit attributes | Approve exports, schema changes |
| Content Lead | Approve and export batches, monitor quality | Schema changes |
| Taxonomy Admin | Schemas, allowed values, unit rules, threshold | Approving exports |
Verify export approval restricted to Content Lead, schema changes restricted to Taxonomy Admin, and direct API access controls.

# AI and Data Quality Validation
Use a golden dataset of items per pilot category with expected attribute values. Target ≥92% correct attribute values; 100% of exported values valid.
- Measure accuracy per attribute and per supplier.
- Analyse wrong-unit errors separately.
- Re-run after schema or model changes.

# Non-Functional Testing

## Performance and scalability
- 10-page spec sheet extracted within 45 seconds.
- Export of 1,000 items within 2 minutes.
- and 25 concurrent specialists.

## Resilience
- Service restart during processing, network interruption, dependency failure, retry/idempotency and recovery from partial failure.
- Backup/restore, data reconciliation after recovery, alerting and runbooks.

## Accessibility and compatibility
- Screen reader labels, keyboard-only navigation, focus order, colour contrast, error identification and zoom/reflow.
- Current enterprise-supported versions of Edge, Chrome and Firefox.

## Security
- Azure AD login, MFA, session timeout, token expiration, logout and JWT validation.
- RBAC at UI and API layers; rate limiting; input validation; safe error messages; CSRF and XSS protection.
- Test malicious PDFs and injection in attribute values (CSV injection with leading '=' must be neutralised).
- Verify SFTP credentials in Key Vault.
- Dependency scanning, SAST/DAST and penetration testing before release.

# Audit and Observability
Verify structured logs, metrics, traces, correlation IDs, dashboards and alerts. Audit records must capture user, role, item number, attribute, old and new value, confidence, model and schema version, approval and export batch. Confirm timestamps, access controls, retention and exportability.

# Test Data and Environment Strategy
- Valid: Golden items for wire and cable, lighting and circuit breakers
- Invalid: Corrupt and oversized PDFs, wrong item numbers
- Boundary – Confidence 79/80%, 1,000/1,001 items, range edges
- Security: CSV-injection strings, restricted roles
- Production-like: Masked spec sheets at pilot volume
Isolated development, QA/integration, performance and UAT environments; versioned test data and expected results; record build, configuration, dataset and model version for every execution.

# Suspension, Entry and Exit Criteria

## Entry criteria
- BRD approved and requirements baselined; acceptance criteria and thresholds agreed.
- Environment, integrations, monitoring and access provisioned; test data available.
- Pilot category schemas finalised; PIM test import location available.
- Build deployed with unit-test evidence and known limitations documented.

## Exit criteria
- At least 95% of planned test cases passed, with all critical-path cases passed.
- No open Critical defects and no open High-severity security defects.
- ≥92% attribute accuracy on golden set.
- Export imports into PIM test without errors.
- Performance targets met.
- All UAT scenarios approved and business sign-off completed.

# Defect Severity & Process
| Severity | Definition | Example |
|---|---|---|
| Critical | Wrong value exported as valid | Amperage exported in wrong unit |
| High | Export blocked | CSV rejected by PIM |
| Medium | Workaround | One supplier layout needs manual entry |
| Low | Cosmetic | Source page link misaligned |
Each defect includes steps, expected/actual results, evidence, severity, environment, build, owner and retest result.

# Risk Register
| Risk | Mitigation |
|---|---|
| Supplier layout variety | Golden set across suppliers, review threshold |
| Unit errors | Normalisation tests |
| Schema change | Versioning and regression |
| PIM format mismatch | Early import test |

# Test Metrics
Map every BRD requirement to test cases and evidence. Report weekly planned/executed/passed/failed/blocked cases, coverage by requirement and risk, defect severity and ageing, attribute accuracy, acceptance rate, export success rate, accessibility and security findings and UAT completion.

# Test Schedule
- MVP1: Mar–May 2026
- MVP2: H2 2026
- Test execution and UAT aligned to MVP1 milestones above.

# End-to-End Scenario
- Sign in as Content Specialist.
- Upload spec sheets for an item.
- Verify extracted and normalised attributes.
- Review low-confidence values.
- Content Lead approves export.
- Verify CSV and PIM test import.
- Verify audit trail.
Go/No-Go: MVP1 should not be released until the exit criteria are met or deviations are accepted by Digital Commerce and Product.